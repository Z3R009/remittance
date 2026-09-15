from odoo import models


from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    summary_section = fields.Selection(
        [
            ('main', 'Main Office'),
            ('nc_tida', 'NC TIDA'),
            ('carp', 'CARP'),
        ],
        string="Summary Section",
        default='main',
        help="Which block this office appears under on the Payroll Summary report.",
    )

    def get_top_parent(self):
        self.ensure_one()
        dept = self
        while dept.parent_id:
            dept = dept.parent_id
        return dept