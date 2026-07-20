from odoo import fields, models, api
from datetime import date

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
    
    gsis_policy_loan = fields.Monetary(
        string="GSIS Policy Loan",
        currency_field="currency_id",
    )
    
    gsis_reg_opt = fields.Monetary(
        string="GSIS REG/OPT",
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

    # ===== METADATA =====
    notes = fields.Text(string="Notes")

    # ===== COMPUTATIONS =====
    @api.depends(
        'gsis_rlip', 'gsis_conso_loan', 'gsis_mpl', 'gsis_emergency_loan', 'gsis_computer_loan', 'gsis_educ_loan', 'gsis_solar_loan',
         'gsis_policy_loan', 'gsis_reg_opt', 'gsis_opt_life_pre', 'gsis_mpl_lite', 'gsis_rel', 'gsis_gfal_2'
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
                (rec.gsis_policy_loan or 0) +
                (rec.gsis_reg_opt or 0) +
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

    _sql_constraints = [
        ('unique_employee_deduction', 
         'unique(employee_id)', 
         'This employee already has a deduction record!'),
    ]