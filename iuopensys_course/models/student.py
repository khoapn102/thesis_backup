from openerp import models, fields, api
from datetime import datetime, date
from openerp.exceptions import ValidationError, Warning

class Student(models.Model):
    
    _inherit = 'student'
    
    # Course list referenced to student
    student_course_ids = fields.One2many('student.course', 'student_id',
                                         string='Courses') # domain=[('offer_course_id.is_lab','=',False)])
    year_batch_id = fields.Many2one('year.batch', string='Batch',
                                    related='academic_year_id.year_batch_id',
                                    store=True)
    student_balance = fields.Float('Student Balance', default=0.0)
    
    # Student Finance Situation
    
    
    # Student Academic Program
    std_academic_prog_id = fields.Many2one('student.academic.program',string='Academic Program',
                                           related='major_id.std_academic_prog_id',
                                           readonly=True)
    standard_grad_date = fields.Char('Std. Graduation Date (at IU)', compute='get_grad_date')
    max_grad_date = fields.Char('Maximum Expectation (at IU)', compute='get_grad_date')
    
    academic_status = fields.Selection(selection=[('regular', 'Regular'),
                                                  ('suspended', 'Suspended'),
                                                  ('expelled', 'Expelled')],
                                       string='Academic Status', default='regular')
    
    is_eng_req = fields.Boolean('Require IE')
    eng_curriculum_id = fields.Many2one('iu.curriculum', string='English Curriculum')
    is_eng_complete = fields.Boolean('Complete IE')
        
    @api.constrains('is_eng_req')
    def _check_eng_curriculum(self):
        for record in self:
            if record.is_eng_req:
                if not record.eng_curriculum_id:
                    raise ValidationError('IE Curriculum cannot be left empty')
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args += ['|',('name', operator, name),('studentId', operator, name)]
        return super(Student,self)._name_search(name='', args=args,
                                                operator='ilike', limit=limit,
                                                name_get_uid=name_get_uid)
    
    # Base on the Graduation Year from IU ACADEMIC PROG        
    @api.depends('std_academic_prog_id','academic_year_id')
    def get_grad_date(self):
        for record in self:
            if record.academic_year_id and record.std_academic_prog_id:
                if record.std_academic_prog_id.program_type == 'iu':
                    record.standard_grad_date = int(record.year_batch_id.year) +\
                            record.std_academic_prog_id.std_grad_year
                    record.max_grad_date = int(record.year_batch_id.year) +\
                            record.std_academic_prog_id.max_grad_year
                elif record.std_academic_prog_id.program_type == 'foreign':
                    record.standard_grad_date = int(record.year_batch_id.year) +\
                            record.std_academic_prog_id.study_year_first
                    record.max_grad_date = int(record.year_batch_id.year) +\
                            int(record.std_academic_prog_id.study_year_first)*2
                
                
                
                
                
            