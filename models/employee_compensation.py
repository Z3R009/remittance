from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EmployeeCompensation(models.Model):
    _name = "employee.compensation"
    _description = "Employee Compensation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
    )

    department_id = fields.Many2one(
            "hr.department",
            string="Department",
            required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="employee_id.company_id.currency_id",
        readonly=True,
        store=True,
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    locked = fields.Boolean(
        string="Locked",
        default=False,
        help="Once locked, this month's compensation can no longer be edited.",
    )

    basic_salary = fields.Monetary(
        string="Basic Salary",
        currency_field="currency_id",
    )

    pera = fields.Monetary(
        string="PERA",
        currency_field="currency_id",
    )

    gross_earnings = fields.Monetary(
        string="Gross Earnings",
        compute="_compute_gross_earnings",
        store=True,
        currency_field="currency_id",
    )

    withholding_tax = fields.Monetary(
        string="Withholding Tax",
        currency_field="currency_id",
    )

    representation_allowance = fields.Monetary(
        string="Representation Allowance",
        currency_field="currency_id",
        tracking=True
    )

    transportation_allowance = fields.Monetary(
        string="Transportation Allowance",
        currency_field="currency_id",
        tracking=True
    )

    _unique_employee_month = models.Constraint(
        'unique(employee_id, payroll_month)',
        'This employee already has a compensation record for this payroll month!',
    )

    @api.depends('basic_salary', 'pera')
    def _compute_gross_earnings(self):
        for rec in self:
            rec.gross_earnings = (rec.basic_salary or 0) + (rec.pera or 0)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.basic_salary = rec.employee_id.wage or 0
                rec.pera = rec.employee_id.pera or 0
                rec.withholding_tax = rec.employee_id.withholding_tax or 0
                rec.department_id = rec.employee_id.department_id

    def write(self, vals):
        protected_fields = {'basic_salary', 'pera', 'withholding_tax', 'employee_id', 'payroll_month'}
        if protected_fields.intersection(vals.keys()):
            for rec in self:
                if rec.locked:
                    raise UserError(
                        "This payroll month (%s) is locked for %s. Unlock it first to make changes."
                        % (rec.payroll_month.strftime('%B %Y'), rec.employee_id.name)
                    )
        return super().write(vals)

    def action_lock(self):
        self.write({'locked': True})

    def action_unlock(self):
        self.write({'locked': False})

    def action_carry_forward(self):
        self.ensure_one()
        next_month = self.payroll_month + relativedelta(months=1)

        existing = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('payroll_month', '=', next_month),
        ], limit=1)
        if existing:
            raise UserError(
                "%s already has a compensation record for %s."
                % (self.employee_id.name, next_month.strftime('%B %Y'))
            )

        # Fresh values pulled from the employee record NOW — not copied from
        # this old record — so a wage change only affects the new month.
        # skip_auto_related_records: don't let create() auto-generate a
        # blank Deduction/Take Home Pay here — we carry the real ones
        # forward properly below instead.
        new_comp = self.with_context(skip_auto_related_records=True).create({
            'employee_id': self.employee_id.id,
            'payroll_month': next_month,
        })

        # Cascade: carry the matching Deduction (and its Take Home Pay) forward too
        old_deduction = self.env['employee.deduction'].search([
            ('employee_id', '=', self.employee_id.id),
            ('payroll_month', '=', self.payroll_month),
        ], limit=1)
        if old_deduction:
            next_deduction_exists = self.env['employee.deduction'].search([
                ('employee_id', '=', self.employee_id.id),
                ('payroll_month', '=', next_month),
            ], limit=1)
            if not next_deduction_exists:
                old_deduction.action_carry_forward()
        else:
            # No deduction existed for the old month either — create blank
            # ones so Compensation/Deduction/Take Home Pay stay in sync.
            deduction = self.env['employee.deduction'].create({
                'employee_id': self.employee_id.id,
                'payroll_month': next_month,
            })
            self.env['take.home.pay'].create({
                'employee_id': self.employee_id.id,
                'payroll_month': next_month,
                'employee_deduction_id': deduction.id,
                'employee_compensation_id': new_comp.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.compensation',
            'view_mode': 'form',
            'res_id': new_comp.id,
            'target': 'current',
        }

    def create_missing_compensations(self):
        Employee = self.env["hr.employee"]

        for employee in Employee.search([]):
            if not self.search([("employee_id", "=", employee.id)], limit=1):
                self.create({
                    "employee_id": employee.id,
                })

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(vals['employee_id'])
                vals.setdefault('basic_salary', employee.wage or 0)
                vals.setdefault('pera', employee.pera or 0)
                vals.setdefault('withholding_tax', employee.withholding_tax or 0)
                vals.setdefault('department_id', employee.department_id.id)

        records = super().create(vals_list)

        if self.env.context.get('skip_auto_related_records'):
            return records

        for record in records:
            if record.employee_id:
                Deduction = self.env["employee.deduction"]
                deduction = Deduction.search([
                    ("employee_id", "=", record.employee_id.id),
                    ("payroll_month", "=", record.payroll_month),
                ], limit=1)
                if not deduction:
                    deduction = Deduction.create({
                        "employee_id": record.employee_id.id,
                        "payroll_month": record.payroll_month,
                    })

                TakeHome = self.env["take.home.pay"]
                take_home = TakeHome.search([
                    ("employee_id", "=", record.employee_id.id),
                    ("payroll_month", "=", record.payroll_month),
                ], limit=1)
                if not take_home:
                    TakeHome.create({
                        "employee_id": record.employee_id.id,
                        "payroll_month": record.payroll_month,
                        "employee_deduction_id": deduction.id,
                        "employee_compensation_id": record.id,
                    })

        return records