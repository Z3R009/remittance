from odoo import fields, models


class RemittanceAmount(models.Model):
    _name = "remittance.amount"
    _description = "Actual Remittance per Month"
    _order = "payroll_month desc"

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )

    # Page 1
    rm_philhealth = fields.Monetary(string="PHIC", currency_field="currency_id")
    rm_dti_pf_cont = fields.Monetary(string="DTI-PF Cont.", currency_field="currency_id")
    rm_dti_pf_loan = fields.Monetary(string="DTI-PF Loan", currency_field="currency_id")
    rm_mdbf = fields.Monetary(string="MDBF", currency_field="currency_id")
    rm_dti_eu_dues = fields.Monetary(string="DTI-EU Dues", currency_field="currency_id")
    rm_dti_eu_hmo = fields.Monetary(string="DTI-EU HMO", currency_field="currency_id")
    rm_lbp_dbp = fields.Monetary(string="LBP Salary Loan", currency_field="currency_id")
    rm_globe = fields.Monetary(string="GLOBE", currency_field="currency_id")
    rm_amaphil = fields.Monetary(string="AMAPHIL", currency_field="currency_id")
    rm_whc = fields.Monetary(string="WHC", currency_field="currency_id")

    # Page 2 - GSIS
    rm_gsis_rlip = fields.Monetary(string="SIC (RLIP)", currency_field="currency_id")
    rm_gsis_conso_loan = fields.Monetary(string="Conso Loan", currency_field="currency_id")
    rm_gsis_mpl_lite = fields.Monetary(string="MPL LITE", currency_field="currency_id")
    rm_gsis_mpl = fields.Monetary(string="MPL", currency_field="currency_id")
    rm_gsis_emergency_loan = fields.Monetary(string="E/L", currency_field="currency_id")
    rm_gsis_computer_loan = fields.Monetary(string="CMPL", currency_field="currency_id")
    rm_gsis_educ_loan = fields.Monetary(string="EDU_ASST", currency_field="currency_id")
    rm_gsis_policy_loan_reg = fields.Monetary(string="PL REG", currency_field="currency_id")
    rm_gsis_policy_loan_opt = fields.Monetary(string="PL OPT", currency_field="currency_id")
    rm_gsis_opt_life_pre = fields.Monetary(string="OPT_LIFE", currency_field="currency_id")
    rm_gsis_rel = fields.Monetary(string="R.E.L.", currency_field="currency_id")
    rm_gsis_gfal_2 = fields.Monetary(string="GFAL II", currency_field="currency_id")

    # Page 3 - HDMF
    rm_hdmf_cont1 = fields.Monetary(string="Cont. I", currency_field="currency_id")
    rm_hdmf_mp2 = fields.Monetary(string="Cont. II", currency_field="currency_id")
    rm_hdmf_mpl = fields.Monetary(string="HDMF MPL", currency_field="currency_id")
    rm_hdmf_calamity_loan = fields.Monetary(string="Calamity", currency_field="currency_id")
    rm_hdmf_housing = fields.Monetary(string="Housing", currency_field="currency_id")

    _unique_month = models.Constraint(
        'unique(payroll_month)',
        'Remittance amount for this month already exists.',
    )