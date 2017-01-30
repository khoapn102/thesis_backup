from openerp import fields, models, api


class GpaClassiy(models.Model):

    _name = "gpa.classify"
    _description = "GPA Classification"

    score_start = fields.Float(string="Starting Range")
    score_end = fields.Float(string="Ending Range")

    catez = fields.Selection(string="Categories",
                             selection=[('ex', 'Excellent'),
                                        ('vgd', 'Very Good'),
                                        ('gd', 'Good'),
                                        ('fgd', 'Faily Good'),
                                        ('f', 'Fair'),
                                        ('avg', 'Average'),
                                        ('wk', 'Weak'),
                                        ('rwk', 'Rather Weak'),
                                        ('twk', 'Too Weak')])

#     @api.multi
#     def _validate_range(self):
#         for x in self:
#             if x.catez not in self:
#                 return True
#         return False
    _sql_constraints = [('unique_categories', 'unique(catez)',
                         'You already have it!!')]

    @api.model
    @api.constrains('score_start', 'score_end')
    # Query inside a model
    def _check_overlap_score(self):
        res = self.search([
            ['score_start', '<=', self.score_end],
            ['score_end', '>=', self.score_start]])
        if res:
            raise ValueError('Overlap Range')
