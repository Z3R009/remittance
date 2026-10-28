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
        domain=[('parent_id', '=', False)],
        help="Select every office that shares this payroll number for this month.",
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    payroll_no = fields.Char(
        string="Payroll No.",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('payroll_month'):
                vals['payroll_month'] = fields.Date.to_date(vals['payroll_month']).replace(day=1)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('payroll_month'):
            vals['payroll_month'] = fields.Date.to_date(vals['payroll_month']).replace(day=1)
        return super().write(vals)

    @api.model
    def get_payroll_no(self, department, month):
        """Return the saved record for the top-level office of `department` in `month`."""
        if not department or not month:
            return self.browse()
        return self.search([
            ('department_ids', 'in', department.get_top_parent().id),
            ('payroll_month', '=', month.replace(day=1)),
        ], limit=1)

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