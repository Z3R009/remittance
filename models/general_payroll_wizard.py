from odoo import api, fields, models


class GeneralPayrollWizard(models.TransientModel):
    _name = "general.payroll.wizard"
    _description = "General Payroll - Enter Payroll No."

    payroll_no = fields.Char(string="Payroll No.", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        if active_model and active_ids:
            records = self.env[active_model].browse(active_ids)
            first = records[:1]
            if first and first.department_id and first.payroll_month:
                top_dept = first.department_id.get_top_parent()
                existing = self.env['general.payroll.number'].search([
                    ('department_id', '=', top_dept.id),
                    ('payroll_month', '=', first.payroll_month),
                ], limit=1)
                if existing:
                    res['payroll_no'] = existing.payroll_no
        return res

    def action_print(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        records = self.env[active_model].browse(active_ids)

        first = records[:1]
        if first and first.department_id and first.payroll_month:
            top_dept = first.department_id.get_top_parent()
            existing = self.env['general.payroll.number'].search([
                ('department_id', '=', top_dept.id),
                ('payroll_month', '=', first.payroll_month),
            ], limit=1)
            if existing:
                existing.payroll_no = self.payroll_no
            else:
                self.env['general.payroll.number'].create({
                    'department_id': top_dept.id,
                    'payroll_month': first.payroll_month,
                    'payroll_no': self.payroll_no,
                })

        if active_model == 'take.home.pay':
            report = self.env.ref('remittance.action_report_general_payroll')
        else:
            report = self.env.ref('remittance.action_report_general_payroll_bulk')

            return report.report_action(records.ids, data={'payroll_no': self.payroll_no})