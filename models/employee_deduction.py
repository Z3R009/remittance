from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class EmployeeDeduction(models.Model):
    _name = "employee.deduction"
    _description = "Employee Deductions"
    _order = "employee_id"

    # ===== REFERENCE FIELDS =====
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
    
    currency_id = fields.Many2one(
        "res.currency",
        related="employee_id.company_id.currency_id",
        readonly=True,
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
        help="First day of the month this deduction applies to (e.g. 2026-07-01 for July 2026)",
    )

    withholding_tax = fields.Monetary(
    string="Withholding Tax",
    related="employee_id.withholding_tax",
    currency_field="currency_id",
    readonly=True,
    store=True,
)

    # ===== GSIS DEDUCTIONS (TAB 1) =====
    gsis_rlip = fields.Monetary(
        string="GSIS RLIP",
        currency_field="currency_id",
        help="Retirement/Life Insurance/Provident"
    )
    
    gsis_conso_loan = fields.Monetary(
        string="GSIS Conso Loan",
        currency_field="currency_id",
    )

    gsis_mpl = fields.Monetary(
        string="GSIS MPL",
        currency_field="currency_id",
    )
    
    gsis_emergency_loan = fields.Monetary(
        string="GSIS Emergency Loan/EML",
        currency_field="currency_id",
    )

    gsis_computer_loan = fields.Monetary(
        string="GSIS Computer Loan",
        currency_field="currency_id",
    )

    gsis_educ_loan = fields.Monetary(
        string="GSIS Educational Loan",
        currency_field="currency_id",
    )

    gsis_solar_loan = fields.Monetary(
        string="GSIS Solar Loan",
        currency_field="currency_id",
    )
    
    gsis_policy_loan_reg = fields.Monetary(
        string="GSIS Policy Loan (Regular)",
        currency_field="currency_id",
    )
    
    gsis_policy_loan_opt = fields.Monetary(
        string="GSIS Policy Loan (Optional)",
        currency_field="currency_id",
    )

    gsis_opt_life_pre = fields.Monetary(
        string="GSIS OPT_LIFE/PRE",
        currency_field="currency_id",
    )
    
    gsis_mpl_lite = fields.Monetary(
        string="GSIS MPL/Lite",
        currency_field="currency_id",
    )
    
    gsis_rel = fields.Monetary(
        string="GSIS R.E.L",
        currency_field="currency_id",
    )

    gsis_gfal_2 = fields.Monetary(
        string="GSIS GFAL II",
        currency_field="currency_id",
    )

    # ===== HDMF/PAG-IBIG DEDUCTIONS (TAB 2) =====

    hdmf_cont1 = fields.Monetary(
        string="HDMF CONT. I",
        currency_field="currency_id",
    )

    hdmf_mp2 = fields.Monetary(
        string="HDMF MP2/CONT. II",
        currency_field="currency_id",
    )
    
    hdmf_mpl = fields.Monetary(
        string="HDMF MPL",
        currency_field="currency_id",
    )
    
    hdmf_calamity_loan = fields.Monetary(
        string="HDMF Calamity Loan",
        currency_field="currency_id",
    )
    
    hdmf_housing = fields.Monetary(
        string="HDMF Lot/Housing",
        currency_field="currency_id",
    )

    # ===== OTHER DEDUCTIONS (TAB 3) =====

    philhealth = fields.Monetary(
        string="PHILHEALTH",
        currency_field="currency_id",
    )
    
    globe = fields.Monetary(
        string="Globe",
        currency_field="currency_id",
    )

    dti_pf_cont = fields.Monetary(
        string="DTI-PF Cont.",
        currency_field="currency_id",
    )
    
    mdbf = fields.Monetary(
        string="MDBF",
        currency_field="currency_id",
    )

    dti_pf_loan = fields.Monetary(
        string="DTI-PF Loan",
        currency_field="currency_id",
    )
    
    dti_eu_dues = fields.Monetary(
        string="DTI-EU Dues",
        currency_field="currency_id",
    )
    
    lbp_dbp = fields.Monetary(
        string="LBP/DBP",
        currency_field="currency_id",
    )

    dti_eu_hmo = fields.Monetary(
        string="DTI-EU HMO",
        currency_field="currency_id",
    )

    amaphil = fields.Monetary(
        string="AMAPHIL",
        currency_field="currency_id",
    )
    
    whc = fields.Monetary(
        string="WHC",
        currency_field="currency_id",
    )


    # ===== LOAN TERM TRACKING (Months Paid / Term) =====
    # Set the starting point manually once (e.g. paid=4, term=18);
    # action_carry_forward() auto-increments paid and auto-zeroes the
    # amount once a loan's term is complete.

    gsis_conso_loan_paid = fields.Integer(string="Conso Loan - Months Paid", default=0)
    gsis_conso_loan_term = fields.Integer(string="Conso Loan - Term (Months)", default=0)

    gsis_mpl_paid = fields.Integer(string="MPL - Months Paid", default=0)
    gsis_mpl_term = fields.Integer(string="MPL - Term (Months)", default=0)

    gsis_emergency_loan_paid = fields.Integer(string="Emergency Loan - Months Paid", default=0)
    gsis_emergency_loan_term = fields.Integer(string="Emergency Loan - Term (Months)", default=0)

    gsis_computer_loan_paid = fields.Integer(string="Computer Loan - Months Paid", default=0)
    gsis_computer_loan_term = fields.Integer(string="Computer Loan - Term (Months)", default=0)

    gsis_educ_loan_paid = fields.Integer(string="Educational Loan - Months Paid", default=0)
    gsis_educ_loan_term = fields.Integer(string="Educational Loan - Term (Months)", default=0)

    gsis_solar_loan_paid = fields.Integer(string="Solar Loan - Months Paid", default=0)
    gsis_solar_loan_term = fields.Integer(string="Solar Loan - Term (Months)", default=0)

    gsis_policy_loan_reg_paid = fields.Integer(string="Policy Loan (Regular) - Months Paid", default=0)
    gsis_policy_loan_reg_term = fields.Integer(string="Policy Loan (Regular) - Term (Months)", default=0)

    gsis_policy_loan_opt_paid = fields.Integer(string="Policy Loan (Optional) - Months Paid", default=0)
    gsis_policy_loan_opt_term = fields.Integer(string="Policy Loan (Optional) - Term (Months)", default=0)

    gsis_opt_life_pre_paid = fields.Integer(string="OPT Life Premium - Months Paid", default=0)
    gsis_opt_life_pre_term = fields.Integer(string="OPT Life Premium - Term (Months)", default=0)

    gsis_gfal_2_paid = fields.Integer(string="GFAL II - Months Paid", default=0)
    gsis_gfal_2_term = fields.Integer(string="GFAL II - Term (Months)", default=0)

    gsis_mpl_lite_paid = fields.Integer(string="MPL/Lite - Months Paid", default=0)
    gsis_mpl_lite_term = fields.Integer(string="MPL/Lite - Term (Months)", default=0)

    hdmf_mpl_paid = fields.Integer(string="HDMF MPL - Months Paid", default=0)
    hdmf_mpl_term = fields.Integer(string="HDMF MPL - Term (Months)", default=0)

    hdmf_calamity_loan_paid = fields.Integer(string="Calamity Loan - Months Paid", default=0)
    hdmf_calamity_loan_term = fields.Integer(string="Calamity Loan - Term (Months)", default=0)

    hdmf_housing_paid = fields.Integer(string="Lot/Housing - Months Paid", default=0)
    hdmf_housing_term = fields.Integer(string="Lot/Housing - Term (Months)", default=0)

    dti_pf_loan_paid = fields.Integer(string="DTI-PF Loan - Months Paid", default=0)
    dti_pf_loan_term = fields.Integer(string="DTI-PF Loan - Term (Months)", default=0)

    lbp_dbp_paid = fields.Integer(string="LBP/DBP - Months Paid", default=0)
    lbp_dbp_term = fields.Integer(string="LBP/DBP - Term (Months)", default=0)

    amaphil_paid = fields.Integer(string="AMAPHIL - Months Paid", default=0)
    amaphil_term = fields.Integer(string="AMAPHIL - Term (Months)", default=0)

    whc_paid = fields.Integer(string="WHC - Months Paid", default=0)
    whc_term = fields.Integer(string="WHC - Term (Months)", default=0)

    # ===== COMPUTED TOTALS =====
    total_gsis = fields.Monetary(
        string="Total GSIS",
        compute="_compute_total_gsis",
        store=True,
        currency_field="currency_id",
    )
    
    total_hdmf = fields.Monetary(
        string="Total HDMF",
        compute="_compute_total_hdmf",
        store=True,
        currency_field="currency_id",
    )
    
    total_other = fields.Monetary(
        string="Total Other",
        compute="_compute_total_other",
        store=True,
        currency_field="currency_id",
    )
    
    total_deductions = fields.Monetary(
        string="Total Deductions",
        compute="_compute_total_deductions",
        store=True,
        currency_field="currency_id",
    )
    
    deduction_group = fields.Selection(
        [
            ('gsis', 'GSIS'),
            ('hdmf', 'HDMF/Pag-IBIG'),
            ('other', 'Other Deductions'),
        ],
        string="Deduction Group",
        compute="_compute_deduction_group",
    )

    def action_carry_forward(self):
        self.ensure_one()
        next_month = self.payroll_month + relativedelta(months=1)

        existing = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('payroll_month', '=', next_month),
        ], limit=1)
        if existing:
            raise UserError(
                "%s already has a deduction record for %s."
                % (self.employee_id.name, next_month.strftime('%B %Y'))
            )

        new_deduction = self.copy({'payroll_month': next_month})

        # Advance loan progress: +1 month paid for every active loan;
        # auto-zero the amount once a loan's term is complete.
        loan_fields = [
            'gsis_conso_loan', 'gsis_mpl', 'gsis_emergency_loan', 'gsis_computer_loan',
            'gsis_educ_loan', 'gsis_solar_loan', 'gsis_policy_loan_reg', 'gsis_policy_loan_opt',
            'gsis_opt_life_pre', 'gsis_gfal_2', 'gsis_mpl_lite', 'hdmf_mpl',
            'hdmf_calamity_loan', 'hdmf_housing', 'dti_pf_loan', 'lbp_dbp',
            'amaphil', 'whc',
        ]
        loan_updates = {}
        for fname in loan_fields:
            if self[fname]:
                paid_field = fname + '_paid'
                term_field = fname + '_term'
                new_paid = (self[paid_field] or 0) + 1
                term = self[term_field] or 0
                loan_updates[paid_field] = new_paid
                if term and new_paid >= term:
                    loan_updates[fname] = 0
        if loan_updates:
            new_deduction.write(loan_updates)

        # Carry the matching Take Home Pay record forward too
        old_take_home = self.env['take.home.pay'].search([
            ('employee_deduction_id', '=', self.id),
        ], limit=1)
        if old_take_home:
            next_month_comp = self.env['employee.compensation'].search([
                ('employee_id', '=', self.employee_id.id),
                ('payroll_month', '=', next_month),
            ], limit=1)
            old_take_home.copy({
                'payroll_month': next_month,
                'employee_deduction_id': new_deduction.id,
                'employee_compensation_id': next_month_comp.id if next_month_comp else False,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.deduction',
            'view_mode': 'form',
            'res_id': new_deduction.id,
            'target': 'current',
        }

    # ===== METADATA =====
    notes = fields.Text(string="Notes")

    # ===== COMPUTATIONS =====
    @api.depends(
        'gsis_rlip', 'gsis_conso_loan', 'gsis_mpl', 'gsis_emergency_loan', 'gsis_computer_loan', 'gsis_educ_loan', 'gsis_solar_loan',
         'gsis_policy_loan_reg', 'gsis_policy_loan_opt', 'gsis_opt_life_pre', 'gsis_mpl_lite', 'gsis_rel', 'gsis_gfal_2'
    )
    def _compute_total_gsis(self):
        for rec in self:
            rec.total_gsis = (
                (rec.gsis_rlip or 0) +
                (rec.gsis_conso_loan or 0) +
                (rec.gsis_mpl or 0) +
                (rec.gsis_emergency_loan or 0) +
                (rec.gsis_computer_loan or 0) +
                (rec.gsis_educ_loan or 0) +
                (rec.gsis_solar_loan or 0) +
                (rec.gsis_policy_loan_reg or 0) +
                (rec.gsis_policy_loan_opt or 0) +
                (rec.gsis_opt_life_pre or 0) +
                (rec.gsis_mpl_lite or 0) +
                (rec.gsis_rel or 0) +
                (rec.gsis_gfal_2 or 0) 
            )

    @api.depends('hdmf_cont1', 'hdmf_mp2', 'hdmf_mpl', 'hdmf_calamity_loan', 'hdmf_housing')
    def _compute_total_hdmf(self):
        for rec in self:
            rec.total_hdmf = (
                (rec.hdmf_cont1 or 0) +
                (rec.hdmf_mp2 or 0) +
                (rec.hdmf_mpl or 0) +
                (rec.hdmf_calamity_loan or 0) +
                (rec.hdmf_housing or 0)
            )

    @api.depends(
        'philhealth', 'globe', 'dti_pf_cont', 'mdbf', 'dti_pf_loan', 'dti_eu_dues', 'lbp_dbp', 'dti_eu_hmo', 'amaphil', 'whc'
    )
    def _compute_total_other(self):
        for rec in self:
            rec.total_other = (
                (rec.philhealth or 0) +
                (rec.globe or 0) +
                (rec.dti_pf_cont or 0) +
                (rec.mdbf or 0) +
                (rec.dti_pf_loan or 0) +
                (rec.dti_eu_dues or 0) +
                (rec.lbp_dbp or 0) +
                (rec.dti_eu_hmo or 0) +
                (rec.amaphil or 0) +
                (rec.whc or 0) 
            )

    @api.depends('total_gsis', 'total_hdmf', 'total_other', 'withholding_tax')
    def _compute_total_deductions(self):
        for rec in self:
            rec.total_deductions = (
                (rec.total_gsis or 0) +
                (rec.total_hdmf or 0) +
                (rec.total_other or 0) +
                (rec.withholding_tax or 0)
            )

    def _compute_deduction_group(self):
        """For display purposes - usually empty"""
        for rec in self:
            rec.deduction_group = False

    _unique_employee_month = models.Constraint(
        'unique(employee_id, payroll_month)',
        'This employee already has a deduction record for this payroll month!',
    )