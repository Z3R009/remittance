from odoo import fields, models


class GeneralPayrollNumber(models.Model):
    _name = "general.payroll.number"
    _description = "Saved General Payroll Number (per top-level office, per month)"
    _order = "payroll_month desc"

    department_id = fields.Many2one(
        "hr.department",
        string="Office (Top-Level)",
        required=True,
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
    )

    payroll_no = fields.Char(
        string="Payroll No.",
        required=True,
    )

    _unique_department_month = models.Constraint(
        'unique(department_id, payroll_month)',
        'This office already has a saved payroll number for this month.',
    )