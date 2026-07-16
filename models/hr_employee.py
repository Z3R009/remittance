from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    pera = fields.Monetary(
        string="PERA",
        currency_field="currency_id",
        tracking=True,
    )

    withholding_tax = fields.Monetary(
        string="Withholding Tax",
        currency_field="currency_id",
        tracking=True,
    )

    gross_earnings = fields.Monetary(
        string="Gross Earnings",
        compute="_compute_gross_earnings",
        store=True,
        currency_field="currency_id",
        tracking=True,
    )

    @api.depends("wage", "pera")
    def _compute_gross_earnings(self):
        for rec in self:
            rec.gross_earnings = (rec.wage or 0.0) + (rec.pera or 0.0)

    @classmethod
    def create(cls, vals_list):
        employees = super().create(vals_list)

        Compensation = employees.env["employee.compensation"]
        Deduction = employees.env["employee.deduction"]

        for employee in employees:
            if not Compensation.search([("employee_id", "=", employee.id)], limit=1):
                Compensation.create({
                    "employee_id": employee.id,
                })

            if not Deduction.search([("employee_id", "=", employee.id)], limit=1):
                Deduction.create({
                    "employee_id": employee.id,
                })

        return employees