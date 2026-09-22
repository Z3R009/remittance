from odoo import fields, models

CATEGORY_SELECTION = [
    ('basic_salary', 'Basic Salary'),
    ('pera', 'PERA'),
    ('philhealth', 'PHIC'),
    ('dti_pf_cont', 'DTI-PF Cont'),
    ('dti_pf_loan', 'DTI-PF Loan'),
    ('mdbf', 'MDBF'),
    ('dti_eu_dues', 'DTI-EU Dues'),
    ('dti_eu_hmo', 'DTI-EU HMO'),
    ('lbp_dbp', 'LBP Salary Loan'),
    ('globe', 'GLOBE'),
    ('amaphil', 'AMAPHIL'),
    ('whc', 'WHC'),
    ('gsis_rlip', 'SIC (RLIP)'),
    ('gsis_conso_loan', 'Conso Loan'),
    ('gsis_mpl_lite', 'MPL LITE'),
    ('gsis_mpl', 'GSIS MPL'),
    ('gsis_emergency_loan', 'E/L'),
    ('gsis_computer_loan', 'CMPL'),
    ('gsis_educ_loan', 'EDU_ASST'),
    ('gsis_policy_loan_reg', 'PL REG'),
    ('gsis_policy_loan_opt', 'PL OPT'),
    ('gsis_opt_life_pre', 'OPT_LIFE'),
    ('gsis_rel', 'R.E.L.'),
    ('gsis_gfal_2', 'GFAL II'),
    ('hdmf_cont1', 'HDMF Cont. I'),
    ('hdmf_mp2', 'HDMF Cont. II'),
    ('hdmf_mpl', 'HDMF MPL'),
    ('hdmf_calamity_loan', 'HDMF Calamity'),
    ('hdmf_housing', 'HDMF Housing'),
]


class PayrollSummaryAdjustment(models.Model):
    _name = "payroll.summary.adjustment"
    _description = "Payroll Summary One-Off Adjustment Row"
    _order = "payroll_month desc, name"

    name = fields.Char(
        string="Label",
        required=True,
        help="Shown as the row label, e.g. 'NAME DETAILS'",
    )

    payroll_month = fields.Date(
        string="Payroll Month",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    line_ids = fields.One2many(
        "payroll.summary.adjustment.line",
        "adjustment_id",
        string="Amounts",
    )


class PayrollSummaryAdjustmentLine(models.Model):
    _name = "payroll.summary.adjustment.line"
    _description = "Payroll Summary Adjustment Amount"

    adjustment_id = fields.Many2one(
        "payroll.summary.adjustment",
        required=True,
        ondelete="cascade",
    )

    category_key = fields.Selection(
        CATEGORY_SELECTION,
        string="Category",
        required=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        readonly=True,
    )

    amount = fields.Monetary(string="Amount", currency_field="currency_id")