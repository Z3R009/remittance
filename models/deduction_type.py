from odoo import fields, models

class DeductionType(models.Model):
    _name = "deduction.type"
    _description = "Deduction Type"
    _order = "deduction_group, name"

    name = fields.Char(
        string="Deduction Name",
        required=True,
        help="e.g., GSIS RLIP, HDMF MP2"
    )
    
    code = fields.Char(
        string="Code",
        required=True,
        unique=True,
        help="e.g., GSIS_RLIP, HDMF_MP2"
    )
    
    deduction_group = fields.Selection(
        [
            ('gsis', 'GSIS'),
            ('hdmf', 'HDMF/Pag-IBIG'),
            ('other', 'Other Deductions'),
        ],
        string="Deduction Group",
        required=True,
    )
    
    is_mandatory = fields.Boolean(
        string="Mandatory",
        default=False,
        help="Cannot be disabled by employee"
    )
    
    active = fields.Boolean(default=True)