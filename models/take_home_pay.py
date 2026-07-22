from odoo import fields, models, api


class TakeHomePay(models.Model):
    _name = "take.home.pay"
    _description = "Take Home Pay"


    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="employee_id.company_id.currency_id",
        readonly=True,
    )

    employee_deduction_id = fields.Many2one(
    "employee.deduction"
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

    total_deductions = fields.Monetary(
        string="Total Deductions",
        related="employee_deduction_id.total_deductions",
        readonly=True,
        store=True,
        currency_field="currency_id",
    )

    gsis_rlip = fields.Monetary(
        string="GSIS RLIP",
        related="employee_deduction_id.gsis_rlip",
        currency_field="currency_id",
        help="Retirement/Life Insurance/Provident"
    )

    gsis_conso_loan = fields.Monetary(
        string="GSIS Conso Loan",
        related="employee_deduction_id.gsis_conso_loan",
        currency_field="currency_id",
    )

    gsis_mpl = fields.Monetary(
        string="GSIS MPL",
        related="employee_deduction_id.gsis_mpl",
        currency_field="currency_id",
    )
    
    gsis_emergency_loan = fields.Monetary(
        string="GSIS Emergency Loan/EML",
        related="employee_deduction_id.gsis_emergency_loan",
        currency_field="currency_id",
    )

    gsis_computer_loan = fields.Monetary(
        string="GSIS Computer Loan",
        related="employee_deduction_id.gsis_computer_loan",
        currency_field="currency_id",
    )

    gsis_educ_loan = fields.Monetary(
        string="GSIS Educational Loan",
        related="employee_deduction_id.gsis_educ_loan",
        currency_field="currency_id",
    )

    gsis_solar_loan = fields.Monetary(
        string="GSIS Solar Loan",
        related="employee_deduction_id.gsis_solar_loan",
        currency_field="currency_id",
    )
    
    gsis_policy_loan = fields.Monetary(
        string="GSIS Policy Loan",
        related="employee_deduction_id.gsis_policy_loan",
        currency_field="currency_id",
    )
    
    gsis_reg_opt = fields.Monetary(
        string="GSIS REG/OPT",
        related="employee_deduction_id.gsis_reg_opt",
        currency_field="currency_id",
    )

    gsis_opt_life_pre = fields.Monetary(
        string="GSIS OPT_LIFE/PRE",
        related="employee_deduction_id.gsis_opt_life_pre",
        currency_field="currency_id",
    )
    
    gsis_mpl_lite = fields.Monetary(
        string="GSIS MPL/Lite",
        related="employee_deduction_id.gsis_mpl_lite",
        currency_field="currency_id",
    )
    
    gsis_rel = fields.Monetary(
        string="GSIS R.E.L",
        related="employee_deduction_id.gsis_rel",
        currency_field="currency_id",
    )

    gsis_gfal_2 = fields.Monetary(
        string="GSIS GFAL II",
        related="employee_deduction_id.gsis_gfal_2",
        currency_field="currency_id",
    )

    hdmf_cont1 = fields.Monetary(
        string="HDMF CONT. I",
        related="employee_deduction_id.hdmf_cont1",
        currency_field="currency_id",
    )

    hdmf_mp2 = fields.Monetary(
        string="HDMF MP2/CONT. II",
        related="employee_deduction_id.hdmf_mp2",
        currency_field="currency_id",
    )
    
    hdmf_mpl = fields.Monetary(
        string="HDMF MPL",
        related="employee_deduction_id.hdmf_mpl",
        currency_field="currency_id",
    )
    
    hdmf_calamity_loan = fields.Monetary(
        string="HDMF Calamity Loan",
        related="employee_deduction_id.hdmf_calamity_loan",
        currency_field="currency_id",
    )
    
    hdmf_housing = fields.Monetary(
        string="HDMF Lot/Housing",
        related="employee_deduction_id.hdmf_housing",
        currency_field="currency_id",
    )

    philhealth = fields.Monetary(
        string="PHILHEALTH",
        related="employee_deduction_id.philhealth",
        currency_field="currency_id",
    )
    
    globe = fields.Monetary(
        string="Globe",
        related="employee_deduction_id.globe",
        currency_field="currency_id",
    )

    dti_pf_cont = fields.Monetary(
        string="DTI-PF Cont.",
        related="employee_deduction_id.dti_pf_cont",
        currency_field="currency_id",
    )
    
    mdbf = fields.Monetary(
        string="MDBF",
        related="employee_deduction_id.mdbf",
        currency_field="currency_id",
    )

    dti_pf_loan = fields.Monetary(
        string="DTI-PF Loan",
        related="employee_deduction_id.dti_pf_loan",
        currency_field="currency_id",
    )
    
    dti_eu_dues = fields.Monetary(
        string="DTI-EU Dues",
        related="employee_deduction_id.dti_eu_dues",
        currency_field="currency_id",
    )
    
    lbp_dbp = fields.Monetary(
        string="LBP/DBP",
        related="employee_deduction_id.lbp_dbp",
        currency_field="currency_id",
    )

    dti_eu_hmo = fields.Monetary(
        string="DTI-EU HMO",
        related="employee_deduction_id.dti_eu_hmo",
        currency_field="currency_id",
    )

    amaphil = fields.Monetary(
        string="AMAPHIL",
        related="employee_deduction_id.amaphil",
        currency_field="currency_id",
    )
    
    whc = fields.Monetary(
        string="WHC",
        related="employee_deduction_id.whc",
        currency_field="currency_id",
    )

    total_net_take_home_pay= fields.Monetary(
        string="Total Net Take Home Pay",
        compute="_compute_total_net_take_home_pay",
        store=True,
        currency_field="currency_id",
    )

    total_net_1st= fields.Monetary(
        string="1st Half",
        compute="_compute_total_net_1st",
        store=True,
        currency_field="currency_id",
    )

    total_net_2nd= fields.Monetary(
        string="2nd Half",
        compute="_compute_total_net_2nd",
        store=True,
        currency_field="currency_id",
    )



    # compute

    @api.depends('basic_salary', 'pera', 'gross_earnings', 'withholding_tax', 'total_deductions', 'gsis_rlip', 'gsis_conso_loan', 'gsis_mpl', 'gsis_emergency_loan', 'gsis_emergency_loan', 'gsis_computer_loan', 'gsis_educ_loan', 'gsis_solar_loan', 'gsis_policy_loan',
                 'gsis_reg_opt', 'gsis_opt_life_pre', 'gsis_mpl_lite', 'gsis_rel', 'gsis_gfal_2',
                 'hdmf_cont1', 'hdmf_mp2', 'hdmf_mpl', 'hdmf_calamity_loan', 'hdmf_housing', 
                 'philhealth', 'globe', 'dti_pf_cont', 'mdbf', 'dti_pf_loan', 'dti_eu_dues', 'lbp_dbp', 'dti_eu_hmo', 'amaphil', 'whc')

    def _compute_total_net_take_home_pay(self):
        for rec in self:
            rec.total_net_take_home_pay = (

                    (rec.basic_salary or 0) +
                    (rec.pera or 0) -
                    (rec.withholding_tax or 0) -
                    (rec.gsis_rlip or 0) -
                    (rec.gsis_conso_loan or 0) -
                    (rec.gsis_mpl or 0) -
                    (rec.gsis_emergency_loan or 0) -
                    (rec.gsis_computer_loan or 0) -
                    (rec.gsis_educ_loan or 0) -
                    (rec.gsis_solar_loan or 0) -
                    (rec.gsis_policy_loan or 0) -
                    (rec.gsis_reg_opt or 0) -
                    (rec.gsis_opt_life_pre or 0) -
                    (rec.gsis_mpl_lite or 0) -
                    (rec.gsis_rel or 0) -
                    (rec.gsis_gfal_2 or 0) -
                    (rec.hdmf_cont1 or 0) -
                    (rec.hdmf_mp2 or 0) -
                    (rec.hdmf_mpl or 0) -
                    (rec.hdmf_calamity_loan or 0) -
                    (rec.hdmf_housing or 0) -
                    (rec.philhealth or 0) -
                    (rec.globe or 0) -
                    (rec.dti_pf_cont or 0) -
                    (rec.mdbf or 0) -
                    (rec.dti_pf_loan or 0) -
                    (rec.dti_eu_dues or 0) -
                    (rec.lbp_dbp or 0) -
                    (rec.dti_eu_hmo or 0) -
                    (rec.amaphil or 0) -
                    (rec.whc or 0)
            )


    @api.depends('basic_salary', 'pera', 'gross_earnings', 'withholding_tax', 'total_deductions', 'gsis_rlip', 'gsis_conso_loan', 'gsis_mpl', 'gsis_emergency_loan', 'gsis_emergency_loan', 'gsis_computer_loan', 'gsis_educ_loan', 'gsis_solar_loan', 'gsis_policy_loan',
                 'gsis_reg_opt', 'gsis_opt_life_pre', 'gsis_mpl_lite', 'gsis_rel', 'gsis_gfal_2',
                 'hdmf_cont1', 'hdmf_mp2', 'hdmf_mpl', 'hdmf_calamity_loan', 'hdmf_housing', 
                 'philhealth', 'globe', 'dti_pf_cont', 'mdbf', 'dti_pf_loan', 'dti_eu_dues', 'lbp_dbp', 'dti_eu_hmo', 'amaphil', 'whc')
    
    def _compute_total_net_1st(self):
        for rec in self:
            rec.total_net_1st = (
                (
                    (rec.basic_salary or 0) +
                    (rec.pera or 0) -
                    (rec.withholding_tax or 0) -
                    (rec.gsis_rlip or 0) -
                    (rec.gsis_conso_loan or 0) -
                    (rec.gsis_mpl or 0) -
                    (rec.gsis_emergency_loan or 0) -
                    (rec.gsis_computer_loan or 0) -
                    (rec.gsis_educ_loan or 0) -
                    (rec.gsis_solar_loan or 0) -
                    (rec.gsis_policy_loan or 0) -
                    (rec.gsis_reg_opt or 0) -
                    (rec.gsis_opt_life_pre or 0) -
                    (rec.gsis_mpl_lite or 0) -
                    (rec.gsis_rel or 0) -
                    (rec.gsis_gfal_2 or 0) -
                    (rec.hdmf_cont1 or 0) -
                    (rec.hdmf_mp2 or 0) -
                    (rec.hdmf_mpl or 0) -
                    (rec.hdmf_calamity_loan or 0) -
                    (rec.hdmf_housing or 0) -
                    (rec.philhealth or 0) -
                    (rec.globe or 0) -
                    (rec.dti_pf_cont or 0) -
                    (rec.mdbf or 0) -
                    (rec.dti_pf_loan or 0) -
                    (rec.dti_eu_dues or 0) -
                    (rec.lbp_dbp or 0) -
                    (rec.dti_eu_hmo or 0) -
                    (rec.amaphil or 0) -
                    (rec.whc or 0)
                ) / 2
            )

    @api.depends('gross_earnings', 'total_deductions')
    def _compute_total_net_2nd(self):
        for rec in self:
            rec.total_net_2nd = (
            (
                (rec.gross_earnings or 0) - 
                (rec.total_deductions or 0)
            )
            ) / 2



    
    

        

