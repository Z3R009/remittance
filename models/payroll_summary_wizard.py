from odoo import fields, models


class PayrollSummaryWizard(models.TransientModel):
    _name = "payroll.summary.wizard"
    _description = "Print Payroll Summary"

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    def action_print(self):
        self.ensure_one()
        return self.env.ref('remittance.action_report_payroll_summary').report_action(
            self, data={'payroll_month': fields.Date.to_string(self.payroll_month)}
        )