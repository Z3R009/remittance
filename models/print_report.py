from odoo import _, api, fields, models
from odoo.exceptions import UserError

from . import print_helpers as ph

import base64

from dateutil.relativedelta import relativedelta



class PayrollPrintWizard(models.TransientModel):
    _name = "payroll.print.wizard"
    _description = "Print PACSVAL / PER OO / JEV"

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    # JEV
    jev_no = fields.Char(string="JEV No.", default="101-2026-08-019")
    jev_date = fields.Date(string="JEV Date", default=fields.Date.context_today)
    dv_no = fields.Char(string="DV No.", default="PS-26-05-")
    alobs_no = fields.Char(string="ALOBS No.", default="PS-26-05-")
    jev_prepared_by = fields.Char(string="Prepared by", default="JINNARD B. LUBATON")
    jev_prepared_by_position = fields.Char(string="Prepared by (Position)", default="Administrative Aide VI")
    jev_certified_by = fields.Char(string="Certified by", default="NEIL ANTHONY T. MORALA")
    jev_certified_by_position = fields.Char(string="Certified by (Position)", default="Accountant III")

    # PER OO
    oo_prepared_by = fields.Char(string="Prepared by", default="CHARLEY JAY M. SUCGANG")
    oo_prepared_by_position = fields.Char(string="Position", default="Accountant II")

    def _report_data(self):
        self.ensure_one()
        return {
            'payroll_month': fields.Date.to_string(self.payroll_month),
            'jev_no': self.jev_no or '',
            'jev_date': fields.Date.to_string(self.jev_date) if self.jev_date else '',
            'dv_no': self.dv_no or '',
            'alobs_no': self.alobs_no or '',
            'jev_prepared_by': self.jev_prepared_by or '',
            'jev_prepared_by_position': self.jev_prepared_by_position or '',
            'jev_certified_by': self.jev_certified_by or '',
            'jev_certified_by_position': self.jev_certified_by_position or '',
            'oo_prepared_by': self.oo_prepared_by or '',
            'oo_prepared_by_position': self.oo_prepared_by_position or '',
        }

    def _print(self, xmlid):
        self.ensure_one()
        return self.env.ref(xmlid).report_action(self, data=self._report_data())

    def action_print_pacsval(self):
        return self._print('remittance.action_report_pacsval')

    def action_print_per_oo(self):
        return self._print('remittance.action_report_per_oo')

    def action_print_jev(self):
        return self._print('remittance.action_report_jev')

    def action_export_pacsval_xlsx(self):
        """Excel: this month vs last month PACSVAL totals (REGULAR / CARP / NC)."""
        self.ensure_one()
        base = self.env['payroll.print.base']
        prev_month = self.payroll_month - relativedelta(months=1)
        cur_rows = base._load_compare_rows(self.payroll_month)
        if not cur_rows:
            raise UserError(_("No Take Home Pay records found for the selected month."))
        sections = ph.build_pacsval_compare(cur_rows, base._load_compare_rows(prev_month))
        cur_label = self.payroll_month.strftime('%B').upper()
        prev_label = prev_month.strftime('%B').upper()
        attachment = self.env['ir.attachment'].create({
            'name': 'PACSVAL_%s.xlsx' % cur_label,
            'datas': base64.b64encode(ph.build_compare_xlsx(sections, cur_label, prev_label)),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%d?download=true' % attachment.id,
            'target': 'self',
        }   


class PayrollPrintBase(models.AbstractModel):
    _name = "payroll.print.base"
    _description = "Shared loader for the PACSVAL / PER OO / JEV prints"

    @api.model
    def _load_rows(self, payroll_month):
        """One dict per take.home.pay record of the month, main offices only.

        PACSVAL, PER OO and JEV all cover the "main" summary section (NC TIDA
        and CARP are separate funds with their own vouchers), which is what
        makes the JEV cash total equal the PACSVAL total.
        """
        recs = self.env['take.home.pay'].search([('payroll_month', '=', payroll_month)])
        recs = recs.filtered(lambda r: (r.department_id.summary_section or 'main') == 'main')
        if not recs:
            raise UserError(_("No Take Home Pay records found for the main offices in the selected month."))
        rows = []
        for rec in recs:
            emp = rec.employee_id
            row = {f: rec[f] or 0.0 for f in ph.THP_FIELDS}
            row.update(
                name=(emp.name or '').strip(),
                item_no=emp.plantilla_item_no or '',
                sg=emp.salary_grade or 0,
                step=emp.salary_step or 0,
                program=emp.oo_program or '',
            )
            rows.append(row)
        return rows

    @api.model
    def _load_compare_rows(self, payroll_month):
        """Every take.home.pay record of the month (all sections) for the Excel export."""
        recs = self.env['take.home.pay'].search([('payroll_month', '=', payroll_month)])
        return [{
            'section': rec.department_id.summary_section or 'main',
            'emp': rec.employee_id.id,
            'name': (rec.employee_id.name or '').strip(),
            'seq': rec.department_id.summary_sequence or 0,
            'total': (rec.representation_allowance or 0.0)
                     + (rec.transportation_allowance or 0.0)
                     + (rec.total_net_1st or 0.0)
                     + (rec.total_net_2nd or 0.0),
        } for rec in recs]

    @api.model
    def _common_values(self, docids, data):
        data = data or {}
        month = data.get('payroll_month')
        return {
            'doc_ids': docids,
            'doc_model': 'payroll.print.wizard',
            'docs': self.env['payroll.print.wizard'].browse(docids),
            'data': data,
            'fmt': ph.fmt,
            'month_title': ph.month_title(month) if month else '',
            'period_label': ph.period_label(month) if month else '',
        }


class ReportPacsval(models.AbstractModel):
    _name = "report.remittance.report_pacsval"
    _inherit = "payroll.print.base"
    _description = "PACSVAL Report Data"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = self._common_values(docids, data)
        values.update(ph.build_pacsval(self._load_rows((data or {}).get('payroll_month'))))
        return values


class ReportPerOo(models.AbstractModel):
    _name = "report.remittance.report_per_oo"
    _inherit = "payroll.print.base"
    _description = "PER OO Report Data"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = self._common_values(docids, data)
        values.update(ph.build_per_oo(self._load_rows((data or {}).get('payroll_month'))))
        return values


class ReportJev(models.AbstractModel):
    _name = "report.remittance.report_jev"
    _inherit = "payroll.print.base"
    _description = "JEV Report Data"

    @api.model
    def _get_report_values(self, docids, data=None):
        values = self._common_values(docids, data)
        values.update(ph.build_jev(self._load_rows((data or {}).get('payroll_month'))))
        jev_date = (data or {}).get('jev_date')
        if jev_date:
            d = fields.Date.from_string(jev_date)
            values['jev_date_label'] = '%d-%s' % (d.day, d.strftime('%b-%y'))
        else:
            values['jev_date_label'] = ''
        return values