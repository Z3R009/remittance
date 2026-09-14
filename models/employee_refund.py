from odoo import api, fields, models


class EmployeeRefund(models.Model):
    _name = "employee.refund"
    _description = "Deduction Refund"
    _order = "payroll_month desc, employee_id"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    employee_name = fields.Char(
        string="Employee Name",
        related="employee_id.name",
        readonly=True,
        store=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Department",
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="employee_id.company_id.currency_id",
        readonly=True,
    )

    # ===== AUDIT TRAIL =====
    source_deduction_id = fields.Many2one(
        "employee.deduction",
        string="Source Deduction Record",
        domain="[('employee_id', '=', employee_id)]",
        help="The Deduction record this refund is correcting (e.g. an overdeducted month).",
    )

    reason = fields.Text(
        string="Reason",
        help="Why this refund is being issued.",
    )

    # ===== GSIS =====
    refund_mpl = fields.Monetary(string="MPL", currency_field="currency_id")
    refund_emergency_loan = fields.Monetary(string="Emergency Loan", currency_field="currency_id")
    refund_ps_overdeduction = fields.Monetary(string="PS Overdeduction", currency_field="currency_id")
    refund_educ_loan = fields.Monetary(string="Educational Assistance Loan", currency_field="currency_id")
    refund_policy_loan_reg = fields.Monetary(string="PL - Regular", currency_field="currency_id")
    refund_mpl_lite = fields.Monetary(string="MPL LITE", currency_field="currency_id")
    refund_rel = fields.Monetary(string="Real Estate Loan (REL)", currency_field="currency_id")
    refund_gfal_2 = fields.Monetary(string="GFAL II", currency_field="currency_id")

    # ===== HDMF =====
    refund_hdmf_mp2 = fields.Monetary(string="MP 2", currency_field="currency_id")
    refund_hdmf_mpl = fields.Monetary(string="MPL (HDMF)", currency_field="currency_id")
    refund_hdmf_calamity = fields.Monetary(string="Calamity", currency_field="currency_id")
    refund_hdmf_hl = fields.Monetary(string="HL", currency_field="currency_id")
    refund_hdmf_housing = fields.Monetary(string="Housing", currency_field="currency_id")

    # ===== OTHER =====
    refund_dti_pf_loan = fields.Monetary(string="DTI-PF Loan", currency_field="currency_id")
    refund_lbp_dbp = fields.Monetary(string="LBP Salary", currency_field="currency_id")
    refund_globe = fields.Monetary(string="GLOBE", currency_field="currency_id")

    total_refund = fields.Monetary(
        string="Total",
        compute="_compute_total_refund",
        store=True,
        currency_field="currency_id",
    )

    @api.depends(
        'refund_mpl', 'refund_emergency_loan', 'refund_ps_overdeduction', 'refund_educ_loan',
        'refund_policy_loan_reg', 'refund_mpl_lite', 'refund_rel', 'refund_gfal_2',
        'refund_hdmf_mp2', 'refund_hdmf_mpl', 'refund_hdmf_calamity', 'refund_hdmf_hl', 'refund_hdmf_housing',
        'refund_dti_pf_loan', 'refund_lbp_dbp', 'refund_globe',
    )
    def _compute_total_refund(self):
        for rec in self:
            rec.total_refund = (
                (rec.refund_mpl or 0) + (rec.refund_emergency_loan or 0) + (rec.refund_ps_overdeduction or 0) +
                (rec.refund_educ_loan or 0) + (rec.refund_policy_loan_reg or 0) + (rec.refund_mpl_lite or 0) +
                (rec.refund_rel or 0) + (rec.refund_gfal_2 or 0) +
                (rec.refund_hdmf_mp2 or 0) + (rec.refund_hdmf_mpl or 0) + (rec.refund_hdmf_calamity or 0) +
                (rec.refund_hdmf_hl or 0) + (rec.refund_hdmf_housing or 0) +
                (rec.refund_dti_pf_loan or 0) + (rec.refund_lbp_dbp or 0) + (rec.refund_globe or 0)
            )

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('department_id') and vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(vals['employee_id'])
                vals['department_id'] = employee.department_id.id
        return super().create(vals_list)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id