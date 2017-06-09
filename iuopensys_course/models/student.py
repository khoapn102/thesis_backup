from openerp import models, fields, api
from datetime import datetime, date
from openerp.exceptions import ValidationError, Warning

class Student(models.Model):
    
    _inherit = 'student'
    
    # Course list referenced to student
    # One2many Domain is different from Many2many
    # Only for Major Courses, not for Extra Curricular progs
    student_course_ids = fields.One2many('student.course', 'student_id',
                                         string='Courses', domain=['|',('offer_course_id.is_lab','=',False),
                                                                   ('offer_course_id.lab_type','!=','combine'),
                                                                   ('offer_course_id.course_id.is_extra_curricular','=',False)])
    # Student balance and Debt
    student_balance = fields.Float('Student Balance', default=0.0)
    student_debt = fields.Float('Student Debt', compute='get_student_debt')
    
    # Student Finance Situation
    financial_aid_id = fields.Many2one('financial.aid', string='Financial Aid')
    student_tuition_ids = fields.One2many('student.registration', 'student_id',
                                          string='Finance Info')
    
    # Student Academic Program
    std_academic_prog_id = fields.Many2one('student.academic.program',string='Academic Program',
                                           related='major_id.std_academic_prog_id',
                                           readonly=True)
    standard_grad_date = fields.Char('Expected to Graduate (at IU)', compute='get_grad_date')
    max_grad_date = fields.Char('Maximum Expectation (at IU)', compute='get_grad_date')
    
    academic_status = fields.Selection(selection=[('regular', 'Regular'),
                                                  ('suspended', 'Suspended'),
                                                  ('expelled', 'Expelled')],
                                       string='Academic Status', default='regular')
    
    is_eng_req = fields.Boolean('Require IE')
    eng_curriculum_id = fields.Many2one('iu.curriculum', string='English Curriculum')
    is_eng_complete = fields.Boolean('Complete IE', 
                                     help='Only check when completely finished IE Programs/Submitted efficient English proficiency.')
    
    # Student Behavior Point
#     student_behavior_point_ids = fields.One2many('student.behavior.point', 'student_id', string='Behavior Point')    
        
    # Student Status
    exam_status = fields.Boolean('Exam Eligibility', default=True)
    account_status = fields.Boolean('Account Status', default=True)
    
    # Student document
        # Submitted Document
    student_document_ids = fields.One2many('student.document', 'student_id', string='Documents')
        # Not submitted Document
    student_document_not_submit_ids = fields.Many2many('iu.document', string='Uncompleted Documents',
                                                       compute='get_student_document_not_submit')
    
    # Semester GPA
    student_semester_ids = fields.One2many('student.semester', 'student_id',
                                           string='Semester Transcript')
    # Behavior Point Semester
    behavior_point_semester_ids = fields.One2many('student.semester','student_id',
                                                  string='Semester Behavior Point')
    
    # Accumulated GPA
    accumulated_gpa = fields.Float(string='Accumulated GPA', compute='get_accumulated_gpa')
    accumulated_gpa_system_4 = fields.Float(string='Accumulated (Sys. 4)')
    accumulated_credits = fields.Integer(string='Accumulated Credits', compute='get_accumulated_gpa')
    gpa_classification = fields.Selection(selection=[('excellent', 'Excellent'),
                                                     ('verygood', 'Very Good'),
                                                     ('good', 'Good'),
                                                     ('fair', 'Fair'),
                                                     ('average', 'Average'),
                                                     ('weak', 'Weak'),
                                                     ('veryweak', 'Very Weak')],
                                          string='Classification',
                                          compute = 'get_accumulated_gpa')
    
#     @api.onchange('academic_year_id')
#     def onchange_academic_year_id(self):
#         if self.academic_year_id:
#             self.year_batch_id = self.academic_year_id.year_batch_id.id
    
    @api.depends('student_semester_ids','student_course_ids')
    def get_accumulated_gpa(self):
        for record in self:
            accum_cred = 0
            total_gpa = 0
            avg_gpa = 0
            if record.student_semester_ids:
                for std_semester in record.student_semester_ids:
                    accum_cred += std_semester.achieved_credits
                    for std_crs in std_semester.student_course_ids:
                        if std_crs.offer_course_id.course_id.cred_count_type == 'count':
                            total_gpa += std_crs.course_gpa * std_crs.course_credits
                        else:
                            continue
                if accum_cred:
                    avg_gpa = total_gpa/accum_cred
                print '======', total_gpa
            record.accumulated_credits = accum_cred
            record.accumulated_gpa = avg_gpa
                    
    @api.depends('student_document_ids')
    def get_student_document_not_submit(self):
        for record in self:
            doc_ids = []
            # Retrieve all the required Docs from Academic Program
            if record.major_id.std_academic_prog_id:
                
                academic_prog = record.major_id.std_academic_prog_id
                if academic_prog.iu_doc_ids:
                    for doc in academic_prog.iu_doc_ids:
                        doc_ids.append(doc.id)
                     
            if record.student_document_ids:
                for document in record.student_document_ids:
                    if document.is_submit or document.is_stored:
                        doc_id = document.iu_doc_id.id
                        doc_ids.remove(doc_id)
            record.student_document_not_submit_ids = doc_ids
    
    @api.depends('student_tuition_ids')
    def get_student_debt(self):
        for record in self:
            if record.student_tuition_ids:
                debt = 0
                for tuition_id in record.student_tuition_ids:
                    debt += tuition_id.amount_leftover
                record.student_debt = debt
    
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
                
                
                
                
                
            