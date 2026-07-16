from odoo import models, fields, api

class EmployeeDeduction(models.Model):
    _name = "employee.deduction"
    _description = "Employee Deductions"


    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
    )


    