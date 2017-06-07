from openerp import models, fields, api

class StudentBehaviorPoint(models.Model):
    
    _name = 'student.behavior.point'
    _description = 'Student Behavior Point System'
    
    # student
    student_id = fields.Many2one('student', string='Student')
    academic_status = fields.Selection(string='Student Status',
                                      related='student_id.academic_status')
    
    # Semester
    semester_id = fields.Many2one('semester', string='Semester')
    
    # Behavior Points
    learning_score = fields.Integer('Learning Score', default=0, help='GPA achieve >= 70')
    school_score = fields.Integer('School Score',default=0, help='Abide with School\'s Rules')
    social_score = fields.Integer('Social Score', default=0, help='Social Abilities')
    activity_score = fields.Integer('Activities Score', default=0,)
    leading_score = fields.Integer('Management Score', default=0,)
    discipline_score = fields.Integer('Discipline Score', default=0,)
    total_score = fields.Integer('Total Score', compute='get_total_score')
    
    @api.constrains('total_score')
    def validate_total_score(self):
        for record in self:
            if record.total_score > 100:
                raise ValueError('Total Score cannot be greater than 100')
    
    @api.depends('learning_score','school_score','social_score',\
                 'activity_score','leading_score','discipline_score')
    def get_total_score(self):
        for record in self:
            record.total_score = (record.learning_score + record.school_score +\
                                  record.social_score + record.activity_score +\
                                  record.leading_score) - record.discipline_score
                                  