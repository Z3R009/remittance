from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GeneralPayrollNumber(models.Model):
    _name = "general.payroll.number"
    _description = "Saved General Payroll Number (per office group, per month)"
    _order = "payroll_month desc"

    department_ids = fields.Many2many(
        "hr.department",
        string="Offices (Top-Level)",
        required=True,
        help="Select every office that shares this payroll number for this month.",
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
    )

    payroll_no = fields.Char(
        string="Payroll No.",
        required=True,
    )

    @api.constrains('department_ids', 'payroll_month')
    def _check_no_overlap(self):
        for rec in self:
            others = self.search([
                ('id', '!=', rec.id),
                ('payroll_month', '=', rec.payroll_month),
                ('department_ids', 'in', rec.department_ids.ids),
            ])
            if others:
                overlapping = others.department_ids & rec.department_ids
                raise ValidationError(
                    "%s already has a saved payroll number for %s (%s)."
                    % (
                        ', '.join(overlapping.mapped('name')),
                        rec.payroll_month.strftime('%B %Y'),
                        others[0].payroll_no,
                    )
                )