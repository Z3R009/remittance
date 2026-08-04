from odoo import models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    def get_top_parent(self):
        self.ensure_one()
        dept = self
        while dept.parent_id:
            dept = dept.parent_id
        return dept