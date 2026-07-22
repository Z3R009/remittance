from odoo import models, fields, api


class EmployeeCompensation(models.Model):
    _name = "employee.compensation"
    _description = "Employee Compensation"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="employee_id.company_id.currency_id",
        readonly=True,
        store=True,
    )

    basic_salary = fields.Monetary(
        string="Basic Salary",
        related="employee_id.wage",
        currency_field="currency_id",
        readonly=True,
        store=True,
    )

    pera = fields.Monetary(
        string="PERA",
        related="employee_id.pera",
        currency_field="currency_id",
        readonly=True,
        store=True,
    )

    gross_earnings = fields.Monetary(
        string="Gross Earnings",
        related="employee_id.gross_earnings",
        currency_field="currency_id",
        readonly=True,
        store=True,
    )

    withholding_tax = fields.Monetary(
        string="Withholding Tax",
        related="employee_id.withholding_tax",
        currency_field="currency_id",
        readonly=True,
        store=True,
    )

    def create_missing_compensations(self):
        Employee = self.env["hr.employee"]

        for employee in Employee.search([]):
            if not self.search([("employee_id", "=", employee.id)], limit=1):
                self.create({
                    "employee_id": employee.id,
                })

    @api.model
    def create(self, vals):
        record = super().create(vals)

        if record.employee_id:
            # Create deduction if missing
            Deduction = self.env["employee.deduction"]
            deduction = Deduction.search(
                [("employee_id", "=", record.employee_id.id)],
                limit=1,
            )
            if not deduction:
                deduction = Deduction.create({
                    "employee_id": record.employee_id.id,
                })

            # Create take home pay if missing
            TakeHome = self.env["take.home.pay"]
            if not TakeHome.search(
                [("employee_id", "=", record.employee_id.id)],
                limit=1,
            ):
                TakeHome.create({
                    "employee_id": record.employee_id.id,
                    "employee_deduction_id": deduction.id,
                })

        return record