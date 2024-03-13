from odoo import models, fields, api

class Ranking(models.Model):
    _name = 'emp.ranking'
    _description = 'Xếp Hạng'

    name = fields.Many2one('hr.employee', string='Ho va Ten')
    performance_score = fields.Integer(string='Performance Score')
    ranking = fields.Selection(
        [('xuat sac', 'Xuat sac'), ('gioi', 'Gioi'), ('trung binh', 'Trung binh'), ('kem', 'Kem')],
        string='Ranking',
        default='xuat sac',
    )
    ranking_sort = fields.Integer(string='Ranking', compute='_compute_ranking', store=True)

    @api.onchange('performance_score')
    def change_ranking(self):
        if self.performance_score >= 90:
            self.ranking = 'xuat sac'
        elif self.performance_score >= 70:
            self.ranking = 'gioi'
        elif self.performance_score >= 50:
            self.ranking = 'trung binh'
        else:
            self.ranking = 'kem'            

    group_ranking = fields.Char(string='Ranking Group', compute='_compute_group_ranking', store=True)

    @api.depends('ranking')
    def _compute_group_ranking(self):
        for employee in self:
            if employee.ranking == 'xuat sac':
                employee.group_ranking = 'Excellent Group'
            elif employee.ranking == 'gioi':
                employee.group_ranking = 'Good Group'
            elif employee.ranking == 'trung binh':
                employee.group_ranking = 'Average Group'
            else:
                employee.group_ranking = 'Poor Group'

    # Xếp hạng các nhân viên theo thứ tự từ 1-n
    @api.depends('performance_score', 'name')
    def _compute_ranking(self):
        all_employees = self.search([])  # Tìm tất cả các nhân viên
        sorted_records = all_employees.sorted(key=lambda r: (r.performance_score, r.name), reverse=True)  
        for i, record in enumerate(sorted_records):
            record.ranking_sort = i + 1
        
    # Khi xóa thì cập nhật lại xếp hạng
    def unlink(self):
        # Lấy tất cả nhân viên trước khi xóa
        employees_before_deletion = self.search([])
        # Thực hiện xóa bản ghi
        res = super(Ranking, self).unlink()
        
        employees_after_deletion = self.search([])       
        # Kiểm tra xem có thay đổi về các nhân viên hay không
        if employees_before_deletion != employees_after_deletion:
            employees_after_deletion._compute_ranking()      
        self.sudo()._compute_ranking()
        return res
