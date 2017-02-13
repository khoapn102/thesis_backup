from openerp import models, fields, api

class Student(models.Model):
    
    _inherit = 'student'
    
    # Course list referenced to student
    student_course_ids = fields.One2many('student.course', 'student_id',
                                         string='Courses')
    year_batch_id = fields.Many2one('year.batch', string='Batch',
                                    related='academic_year_id.year_batch_id',
                                    store=True)
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args += ['|',('name', operator, name),('studentId', operator, name)]
        return super(Student,self)._name_search(name='', args=args,
                                                operator='ilike', limit=limit,
                                                name_get_uid=name_get_uid)
        
        
