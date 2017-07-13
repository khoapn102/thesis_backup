from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError, Warning

class Student(models.Model):
    
    _inherit = 'student'
    
    student_log_ids = fields.One2many('student.log', 'student_id', string='Logs')
    
    # Graduation Prog
    
    major_course_complete_ids = fields.One2many('student.course', 'student_id', string='Completed Courses',
                                                 domain=['|',('offer_course_id.is_lab','=',False),
                                                           ('offer_course_id.lab_type','!=','combine'),
                                                           ('offer_course_id.course_id.is_extra_curricular','=',False),
                                                           ('is_complete', '=', True)]) # only check if course is completed
    # Major Incomplete
    major_course_not_complete_ids = fields.Many2many('course', string='Incompleted Courses',
                                               compute='get_all_course_details')
    major_total_credits = fields.Integer(related='major_id.major_total_credits')
    major_total_not_count_credits = fields.Integer(related='major_id.major_total_not_count_credits')
    major_not_count_achieved_credits = fields.Integer(string='Achieved P/F', compute='get_all_course_details')
    major_incomplete_credits = fields.Integer(string='Missing Credits', compute='get_all_course_details')
    major_achieved_credits = fields.Integer(string='Achieved Credits', compute='get_all_course_details',
                                            help='Total achieved credits during studying duration.')
    major_accumulated_credits = fields.Integer(string='Accumulated Credits', compute='get_all_course_details',
                                               help='Total accumulated credits counted toward Curriculum. Only credits from curriculum is counted')
    major_total_not_count_credits = fields.Integer(related='major_id.major_total_not_count_credits')
    major_total_with_no_count_credits = fields.Integer(related='major_id.major_total_with_no_count_credits')
        
    # Program Incomplete
    academic_program_course_not_complete_ids = fields.Many2many('course', string='Incomplete Programs',
                                                                compute='get_all_program_details')
    academic_program_course_complete_ids = fields.One2many('student.course', 'student_id', string='Completed Programs',
                                                           domain=[('offer_course_id.course_id.is_extra_curricular','=',True),
                                                                   ('is_complete','=',True)])
    
    empty_major_course_ids = fields.Many2many('course', string='Empty',
                                              help='If student has completed all major courses, no more course will be shown here.')
    
    # New - Graduation 
#     major_course_not_complete_ids = fields.Many2many('course',string='Incompleted Courses',
#                                                      default='get_default_all_course_details')
#     major_course_complete_ids = fields.Many2many('course', string='Completed Courses')
#     major_incomplete_credits = fields.Ingteger(string='Missing Credits', compute='get_all_credits')
#     major_achieved_credits = fields.Integer(string='Achieved Credits', compute='get_all_credits')
    
    
    graduation_status = fields.Selection(selection=[('ie', 'IE Program'),
                                                    ('ontrack','On Track'),
                                                    ('complete', 'Complete Required Program'),
                                                    ('readygrad', 'Ready for Graduation/Transfer'),
                                                    ('graduated', 'Graduated/Transferred')],
                                         string='Graduation Status',
                                         default='ontrack')
    
    graduation_date = fields.Date(string='Graduation Date')
    
    trigger_grad_status = fields.Boolean('Trigger', compute='calculate_grad_status')
    
    @api.multi
    def calculate_grad_status(self):
        for record in self:
            if record.major_incomplete_credits:
                record.trigger_grad_status = False
            else:
                record.trigger_grad_status = True
    
    @api.multi
    def write(self, vals):
        """
        1. If any field is updated for student
        2. -> will write to log file both old and new value 
        3. -> determine base on 
        """
        for record in self:
            if vals:
                
                # Check if student has changed certain major/department
                # If Department change -> Major and Academic Year must be changed
                
                if 'department_id' in vals or 'major_id' in vals:
                    print '====== HERE'
                    if 'department_id' in vals:
                        if record.major_id.department_id.id != vals['department_id'] or\
                            record.academic_year_id.department_id.id != vals['department_id']:
                            if ('major_id' not in vals or 'academic_year_id' not in vals):
                                raise ValidationError('Major and Class must be changed according to Department.')
                    
                    no_change_lst = []
                    dept = ''
                    major = ''
                    if 'department_id' in vals:
                        dept = self.env['department'].search([('id','=',vals['department_id'])]).name
                    if 'major_id' in vals:
                        major = self.env['major'].search([('id','=',vals['major_id'])]).name                    
                    
                    student_logs = self.env['student.log'].search([('student_id','=',record.id)])
#                     print '======', student_logs
                    if student_logs:
                        for log in student_logs:
                            # Any log with old value is the current changing value in VALS -> Stop
                            if log.old_value == (dept or major):
#                                 print '++++++ No change Dept/Major.'
                                raise ValidationError('Student cannot change back to this Department/Major.')                            
                
                tf_map = {True:'Yes',
                          False:'No'}
                
                model_map = { 'department_id': ('Department','department', record.department_id.name),
                              'major_id': ('Major', 'major', record.major_id.name),
                              'std_academic_prog_id': ('Academic Program', 'student.academic.program', record.std_academic_prog_id.name),
                              'academic_year_id': ('Class', 'academic.year', record.academic_year_id.name),
                              'year_batch_id': ('Batch', 'year.batch', record.year_batch_id.name),
                              'financial_aid_id': ('Financial Aid', 'financial.aid', record.financial_aid_id.name),
                              'eng_curriculum_id': ('IE Program', 'iu.curriculum', record.eng_curriculum_id.name),}
                
                # Selection Field
                academic_status = dict(self.env['student']._columns['academic_status'].selection)
                
                no_model_map = {
                                'academic_status': ('Academic Status',academic_status[record.academic_status]),
                                'studentId': ('Student ID', record.studentId),
                                'exam_status': ('Exam Eligible', tf_map[record.exam_status]),
                                'is_eng_req': ('IE Required', tf_map[record.is_eng_req]),
                                'is_eng_complete': ('IE Completed', tf_map[record.is_eng_complete])
                                }
                
                for item in vals:
#                     print '=======', item
                    if item in ['department_id','major_id','std_academic_prog_id',
                                'academic_year_id','year_batch_id','financial_aid_id',
                                'eng_curriculum_id','academic_status','studentId',
                                'exam_status','is_eng_req','is_eng_complete']:
                        field_change = item
                        student_id = record.id
                        modified_user_id = self.env.user.id
                        modified_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        field_change_name = ''
                        old_value = ''
                        new_value = ''
                        
                        # For Model Mapping
                        if item in model_map:
                            field_change_name = model_map[item][0]
                            old_value = model_map[item][2]
                            model = model_map[item][1]
                            model_id = self.env[model].search([('id','=',vals[item])])
                            if model_id:
                                new_value = model_id.name
                        
                        # For none model Mapping- values, integer, selection, float ..                  
                        elif item in no_model_map:
                            field_change_name = no_model_map[item][0]
                            old_value = no_model_map[item][1]
                            if item == 'academic_status':
                                new_value = academic_status[vals[item]]
                            else:
#                                 if tf_map[vals[item]]:
#                                     new_value = tf_map[vals[item]]
#                                 else:
                                if item in ['exam_status', 'is_eng_req','is_eng_complete']:
                                    new_value = tf_map[vals[item]]
                                else:
                                    new_value = vals[item]
                            
                        new_vals = {'student_id':student_id,
                                    'modified_user_id': modified_user_id,
                                    'field_change': field_change,
                                    'field_change_name': field_change_name,
                                    'modified_date': modified_date,
                                    'old_value':old_value,
                                    'new_value':new_value,
                                    }
#                         print '=======', new_vals
                        self.env['student.log'].create(new_vals)
                    else:
                        continue
                        
        return super(Student,self).write(vals)
    
    # Button Status Functions
    @api.one
    def set_ready_to_graduate(self):
        self.write({'graduation_status':'readygrad'})
    
    @api.one
    def set_graduated(self):
        self.write({'graduation_status':'graduated'})
    
    @api.one
    def set_ontrack(self):
        self.write({'graduation_status':'ontrack'})
        
    @api.one
    def set_complete_major(self):
        self.write({'graduation_status':'complete'})
    
    # Button Print Transcript
    @api.multi
    def print_student_transcript(self):
        report_name = 'iuopensys_studentlog.report_student_transcript'
        return self.env['report'].get_action(self, report_name)
    
    # Button Print Student Progress
    @api.multi
    def print_student_progress(self):
        report_name = 'iuopensys_studentlog.report_student_progress'
        return self.env['report'].get_action(self, report_name)
    
    # Change status from IE to Ontrack/Complete
    @api.onchange('is_eng_req')
    def onchange_is_eng_req(self):
        if self.graduation_status != 'ie' and self.is_eng_req:
            self.graduation_status = 'ie'
        else:
            self.graduation_status = 'ontrack'
        if self.eng_curriculum_id:
            self.eng_curriculum_id = False
        
    @api.onchange('is_eng_complete')
    def onchange_is_eng_complete(self):
        if self.is_eng_req and self.eng_curriculum_id:
            if self.is_eng_complete:
                if self.graduation_status == 'ie':
                    if self.major_incomplete_credits == 0:
                        self.graduation_status = 'complete'
                    else:
                        self.graduation_status = 'ontrack'
            else:
                self.graduation_status = 'ie'
                
    # Manage IU Programs / Extra Curriculars Courses
    @api.depends('academic_program_course_complete_ids')
    def get_all_program_details(self):
        for record in self:
            if record.major_id:
                curr_major = record.major_id
                prog_ids = []
                # Get Academic Program Curriculum (Sinh hoat cong dan, etc.)
                if curr_major.std_academic_prog_id:
                    if curr_major.std_academic_prog_id.req_curriculum_ids:
                        curr_curriculum = curr_major.std_academic_prog_id.req_curriculum_ids
                        for curriculum in curr_curriculum:
                            if curriculum.course_ids:
                                for course in curriculum.course_ids:
                                    prog_ids.append(course.id)
                
                if record.academic_program_course_complete_ids:
                    for program in record.academic_program_course_complete_ids:
                        if program.offer_course_id.course_id.id in prog_ids:
                            prog_ids.remove(program.offer_course_id.course_id.id) # -> update IU Program List
                
                record.academic_program_course_not_complete_ids = prog_ids
        
    # The reason doing this in case major is changed, -> will only calculate the course
    # that belongs to current major's curriculum
    # Manage only Major courses             
    @api.depends('student_course_ids')
    def get_all_course_details(self):
#         for record in self:
#             # Retrieve curriculum
#             if record.major_id:
#                 curr_major = record.major_id
#                 crs_ids = []
#                 accum_crs_ids = []
#                 accum_crs_track = []
# #                 prog_ids = []
#                 complete_crs_ids = []
#                 
#                 # Get Academic Program Curriculum (Sinh hoat cong dan, etc.)
# #                 if curr_major.std_academic_prog_id:
# #                     if curr_major.std_academic_prog_id.req_curriculum_ids:
# #                         curr_curriculum = curr_major.std_academic_prog_id.req_curriculum_ids
# #                         for curriculum in curr_curriculum:
# #                             if curriculum.course_ids:
# #                                 for course in curriculum.course_ids:
# #                                     prog_ids.append(course.id)
#                 
#                 crs_ids = record.major_id.course_ids.ids
#                 
#                 # Get Major Curriculum - All Courses in Major's
#                 if curr_major.iu_curriculum_ids:
#                     for curriculum in curr_major.iu_curriculum_ids:
#                         if curriculum.course_ids:
#                             accum_crs_ids.append((curriculum.course_ids.ids, curriculum.max_cred_require))
#                             accum_crs_track.append((curriculum.course_ids.ids, 0))
#                 print '======== Curr', crs_ids, ' ', accum_crs_ids
#         
#             # Starting, incomplete credits = total major credits
#             incomplete_creds = record.major_total_credits 
#             achieved_creds = 0           
#             passing_grade = self.env['ir.config_parameter'].get_param('iuopensys_course.course_passing_grade')
#             
#             if record.student_course_ids:
#                 # 1. Retrieve all courses in Curriculum of Major
#                 # 2. Compare with the current courses -> which one complete
#                     # Update incomplete_credits
#                     # Update the incomplete course list
#                 # 3. Remove the course from the list. Display           
#             
#                 crs_ids_copy = crs_ids[:] # make copy of major curriculum
#                 
#                 # course_gpa is computed field vs passing_grade ->
#                 # if there is error, check here
#                 # Moreover, course must be in Curriculum to be counted
#                 for student_course in record.student_course_ids:
#                     # Only check course that is complete or with passing grade
#                     if student_course.is_complete or student_course.course_gpa >= float(passing_grade):
#                         
# #                         print 'ID ', student_course.offer_course_id.course_id.id, ' ', student_course.offer_course_id.course_id.name
#                         
#                         if student_course.offer_course_id.course_id.id in crs_ids:
#                             crs_ids.remove(student_course.offer_course_id.course_id.id) # -> update Curriculum list
#                             
#                             complete_crs_ids.append(student_course.offer_course_id.course_id.id)
#                         
#                         # If not Major courses, check with the Academic Program Courses -> remove if needed
# #                         if student_course.offer_course_id.course_id.id in prog_ids:
# #                             prog_ids.remove(student_course.offer_course_id.course_id.id) # -> update IU Program List
#                         
#                         # Only count Course that has Credit option. P/F option will be ignored
#                         # Course that belongs to the curriculum will be counted ->Transferred made
#                         if student_course.offer_course_id.course_id.cred_count_type == 'count' and\
#                             student_course.offer_course_id.course_id.id in crs_ids_copy:
#                             
#                             incomplete_creds -= student_course.offer_course_id.course_id.number_credits
#                             achieved_creds += student_course.offer_course_id.course_id.number_credits
#             
#             record.major_course_not_complete_ids = crs_ids
#             record.major_course_complete_ids = complete_crs_ids
#             record.major_incomplete_credits = incomplete_creds
#             record.major_achieved_credits = achieved_creds 
# #             record.academic_program_course_not_complete_ids = prog_ids       
        for record in self:
            if record.major_id:
                curr_major = record.major_id
                course_ids = curr_major.course_ids.ids # majors' courses
                
                # Curriculum for Major checking 
                curriculum_crs = {}
                  
                incomplete_creds = curr_major.major_total_credits
                achieved_creds = 0
                accumulated_creds = 0
                achieved_pf_creds = 0 # achieved P/F
                
                if curr_major.iu_curriculum_ids:
                    for curriculum in curr_major.iu_curriculum_ids:
                        if curriculum.course_ids:
                            curriculum_crs[tuple(curriculum.course_ids.ids)] = curriculum.max_cred_require
                    
                complete_crs = []
                                                              
                if record.student_course_ids:
                    course_ids_copy = course_ids[:] # Copy course list
                    for student_course in record.student_course_ids:

                        if student_course.is_complete:
                                                        
                            # Check completed course with curriculum. If selection is made between courses, 
                            # Whichever courses completed first will be counted towards the credits.
                            # Curriculum must be well designed to work.
                            
                            # Course is complete, remove and check
                            if student_course.offer_course_id.course_id.id in course_ids_copy:
                                
                                # Count achieved Major Credits
                                if student_course.offer_course_id.course_id.cred_count_type == 'count':
                                    
                                    # Only new course, passed repeat course will not be counted
                                    if student_course.offer_course_id.course_id.id not in complete_crs:
                                        achieved_creds += student_course.offer_course_id.course_id.number_credits
                                    
                                    for item in curriculum_crs:
                                        # Check if course in curriculum and also max_cred is still available
                                        if student_course.offer_course_id.course_id.id in item and curriculum_crs[item] > 0:
                                            curriculum_crs[item] -= student_course.offer_course_id.course_id.number_credits
                                            
                                            # Only new course, passed repeat course will not be counted
                                            if student_course.offer_course_id.course_id.id not in complete_crs:
                                                accumulated_creds += student_course.offer_course_id.course_id.number_credits
                                                
                                elif student_course.offer_course_id.course_id.cred_count_type == 'nocount':
                                    achieved_pf_creds += student_course.offer_course_id.course_id.number_credits
                                
                                if student_course.offer_course_id.course_id.id in course_ids:
                                    course_ids.remove(student_course.offer_course_id.course_id.id)
                            
                            complete_crs.append(student_course.offer_course_id.course_id.id)
                                                                
                record.major_course_not_complete_ids = course_ids
                record.major_achieved_credits = achieved_creds
                record.major_not_count_achieved_credits = achieved_pf_creds
                record.major_accumulated_credits = accumulated_creds
                record.major_incomplete_credits = record.major_total_credits - record.major_accumulated_credits
                
                # Must f5 the page -> get new effect after
                if record.major_incomplete_credits == 0 and record.major_total_credits > 0 and\
                    record.major_not_count_achieved_credits >= record.major_total_not_count_credits:
                    if record.graduation_status == 'ontrack':
                        record.write({'graduation_status':'complete'})
                        
                elif record.major_incomplete_credits > 0:
                    if record.graduation_status != 'ontrack':
                        record.write({'graduation_status':'ontrack'})
    
#     @api.onchange('is_complete_major')
#     def onchange_is_complete_major(self):
#         if self.is_complete_major:
#             if self.graduation_status == 'ontrack':
#                 self.graduation_status = 'complete'
                
#     @api.onchange('student_course_ids')
#     def onchange_student_course_ids(self):
#         if self.student_course_ids:
#             print '=====Missing Creds: ', self.major_incomplete_credits
#             if self.major_incomplete_credits == 0:
#                 print '=======Grad: ', self.graduation_status
#                 if self.graduation_status == 'ontrack':
#                     self.graduation_status = 'complete'
#             else:
#                 self.graduation_status = 'ontrack'
    
#     @api.model
#     def create(self, vals):
#         curr_student = super(Student, self).create(vals)

    # Student Graduatino Status -> Check on following
    # 1. Complete all Majors
    # 2. Complete all required Programs
    # 3. Complete Behavior Point -> Need Behavior Point Standard
    # 4. Submit all Documents
    # 5. No Debt 
#     @api.depends('student_course_ids', 'major_course_not_complete_ids',
#                  'major_course_complete_ids',
#                  'academic_program_course_not_complete_ids',
#                  'student_document_not_submit_ids')
#     def get_graduation_status(self):
#         for record in self:
#             # 3 Stage for each Student
#             # Complete major
#             # 1. For each curriculum -> satisfied max credit ?
#             # 2. If any elective not complete -> cant graduate
#             
#             if record.major_accumulated_credits == record.major_id.major_total_credits:
#                 record.graduation_status = 'donemajor'
#                 if not record.academic_program_course_not_complete_ids:
#                     if not record.student_document_not_submit_ids:
#                         if record.student_debt == 0.0:
#                             record.graduation_status = 'complete'                
#             else:
#                 record.graduation_status = 'ontrack'
        
          
                        
                        
                        
                        
                        
                        
                        
                   
                   
                    