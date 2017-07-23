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
    payment_note = fields.Char(compute='get_payment_note')
    
    tuition_discount_time = fields.Integer('Instant discount times', default=0)
    
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
    
    student_financial_aid_ids = fields.One2many('student.financial.aid','student_id','List of Financial Aids')
    
#     @api.onchange('academic_year_id')
#     def onchange_academic_year_id(self):
#         if self.academic_year_id:
#             self.year_batch_id = self.academic_year_id.year_batch_id.id
    
    @api.depends('tuition_discount_time')
    def get_payment_note(self):
        for record in self:
            if record.tuition_discount_time > 0:
                payment_note = 'Student has received '
                payment_note += str(record.tuition_discount_time)
                payment_note += ' time(s) of instant discount of 10% for paying over 120 million VND (6000 USD) at once.'
                record.payment_note = payment_note
    
    @api.onchange('student_balance')
    def onchange_student_balance(self):
        if self.student_balance and self.student_balance >= self.major_id.std_academic_prog_id.tuition_at_iu:
            if not self.tuition_discount:
                self.tuition_discount = True
        else:
            self.tuition_discount = False
    
    @api.depends('student_semester_ids','student_course_ids')
    def get_accumulated_gpa(self):
        for record in self:
            accum_cred = 0
            total_gpa = 0
            avg_gpa = 0            
            total_creds = 0 # all credits of all semester even failed courses
            
            complete_crs_ids = {} # Keeps track of courses which repeat to improve gpa
                        
            if record.student_semester_ids:
                for std_semester in record.student_semester_ids:
                    
                    accum_cred += std_semester.achieved_credits # OK
                    total_creds += std_semester.total_credits - std_semester.no_count_credits
                    
                    for std_crs in std_semester.student_course_ids:
#                         print '====== HERE', complete_crs_ids,  '=====', total_gpa, '---- course', std_crs.offer_course_id.course_id.id
                        if std_crs.offer_course_id.course_id.cred_count_type == 'count':
                            
                            total_gpa += std_crs.course_gpa * std_crs.course_credits # Add gpa first then check after
                            # If course is completed, save the course_id, credits, gpa into the dict
                            # in dict form: {'course_id': (credits, gpa)}
#                             if std_crs.is_complete:
                            if std_crs.offer_course_id.course_id.id not in complete_crs_ids: # course is new
                                complete_crs_ids[std_crs.offer_course_id.course_id.id] = (std_crs.offer_course_id.number_credits, std_crs.course_gpa,\
                                                                                          std_crs.offer_course_id.id)
                                
                            elif std_crs.offer_course_id.course_id.id in complete_crs_ids: # found repeat course
                                
                                prev_crs_id = self.env['student.course'].search([('student_id','=', record.id),
                                                                                 ('offer_course_id','=',complete_crs_ids[std_crs.offer_course_id.course_id.id][2])])
                                
                                curr_creds = complete_crs_ids[std_crs.offer_course_id.course_id.id][0]
                                curr_gpa = complete_crs_ids[std_crs.offer_course_id.course_id.id][1]
                                total_gpa -= curr_creds * curr_gpa # Remove previous course gpa
                                
                                # Previous course Pass -> take out the credits. because the repeat course will be counted
#                                 if prev_crs_id and prev_crs_id.is_complete:
#                                     accum_cred -= curr_creds # remove accumulated credits
#                                     total_creds -= curr_creds

                                if prev_crs_id:
                                    accum_cred -= curr_creds # remove accumulated credits
                                    total_creds -= curr_creds
                                    
                                    
                                complete_crs_ids[std_crs.offer_course_id.course_id.id] = (std_crs.offer_course_id.number_credits, std_crs.course_gpa)
                        else:
                            continue
#                         print '======= NOW', complete_crs_ids, '-----', total_gpa,' ', accum_cred, ' ', total_creds
                        
#                 print '===== total', total_creds, ' ---- gpa', total_gpa 
#                 if accum_cred and accum_cred == total_creds:
                if total_creds:
                    avg_gpa = total_gpa/total_creds
                elif accum_cred:
                    avg_gpa = total_gpa/accum_cred
                
#                 elif total_creds and accum_cred < total_creds:
#                     avg_gpa = total_gpa/total_creds
            
            record.accumulated_credits = accum_cred
            record.accumulated_gpa = round(avg_gpa,1)
                    
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
                if not record.eng_curriculum_id and not record.is_eng_complete:
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
                
    
    @api.multi
    def write(self, vals):
        for record in self:
            if vals:
                if 'financial_aid_id' in vals and vals['financial_aid_id']:
#                     print '======', vals['financial_aid_id']
                    std_financial_id = self.env['student.financial.aid'].search([('student_id','=',record.id),
                                                                         ('financial_aid_id','=',vals['financial_aid_id'])])
                    # Create new rec student_financial_aid
#                     check = False
                    if not std_financial_id:
                        new_vals = {'student_id':record.id,
                                    'financial_aid_id': vals['financial_aid_id'],
                                    'is_active':True,
                                    }
                        std_finance = self.env['student.financial.aid']
                        std_finance.create(new_vals)
#                         check = True
                    # Thens set inactive of all the rest -> only 1 record activate at one time
                    # Only 1 Scholarship is allowed to student at 1time
                    std_financial_ids = self.env['student.financial.aid'].search([('student_id','=',record.id)])
                    if std_financial_ids:
                        for std_fin in std_financial_ids:
                            if std_fin.financial_aid_id.id == vals['financial_aid_id']:
                                if not std_fin.is_active:
                                    std_fin.write({'is_active':True})
                                continue
                            if std_fin.is_active:
                                std_fin.write({'is_active':False})
                    
        return super(Student,self).write(vals)
    
    @api.model
    def create(self, vals):
        curr_std = super(Student,self).create(vals)
        if vals:
            if 'financial_aid_id' in vals and vals['financial_aid_id']:
#                     print '======', vals['financial_aid_id']
                    std_financial_id = self.env['student.financial.aid'].search([('student_id','=',curr_std.id),
                                                                         ('financial_aid_id','=',vals['financial_aid_id'])])
                    # Create new rec student_financial_aid
#                     check = False
                    if not std_financial_id:
                        new_vals = {'student_id':curr_std.id,
                                    'financial_aid_id': vals['financial_aid_id'],
                                    'is_active':True,
                                    }
                        std_finance = self.env['student.financial.aid']
                        std_finance.create(new_vals)
        return curr_std
                             
                
                
                
            