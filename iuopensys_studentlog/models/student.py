from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError, Warning

class Student(models.Model):
    
    _inherit = 'student'
    
    student_log_ids = fields.One2many('student.log', 'student_id', string='Logs')
    
    # Graduation Prog
    # Major Incomplete
    major_course_not_complete_ids = fields.Many2many('course', string='Incompleted Courses',
                                               compute='get_all_course_details')
    major_course_complete_ids = fields.Many2many('course', string='Completed Courses',
                                                 compute='get_all_course_details')
    major_total_credits = fields.Integer(related='major_id.major_total_credits')
    major_incomplete_credits = fields.Integer(string='Missing Credits', compute='get_all_course_details')
    major_achieved_credits = fields.Integer(string='Achieved Credits', compute='get_all_course_details')
    major_accumulated_credits = fields.Integer(string='Accumulated Credits', compute='get_all_course_details')
    
    # Program Incomplete
    academic_program_course_not_complete_ids = fields.Many2many('course', string='Incomplete Programs',
                                                                compute='get_all_course_details')
    
    graduation_status = fields.Selection(selection=[('ontrack','On Track'),
                                                    ('donemajor', 'Complete Major Program'),
                                                    ('minor', 'Minor Complete'),
                                                    ('complete', 'Ready for Graduation')],
                                         string='Graduation Status',
                                         default='ontrack',
                                         compute='get_graduation_status')
        
    @api.depends('student_course_ids', 'major_course_not_complete_ids',
                 'academic_program_course_not_complete_ids',
                 'student_document_not_submit_ids')
    def get_graduation_status(self):
        for record in self:
            # 3 Stage for each Student
            # Complete major
            
            print True
    
    @api.depends('student_course_ids')
    def get_all_course_details(self):
        for record in self:
            # Retrieve curriculum
            if record.major_id:
                curr_major = record.major_id
                crs_ids = []
                prog_ids = []
                complete_crs_ids = []
                
                # Get Academic Program Curriculum (Sinh hoat cong dan, etc.)
                if curr_major.std_academic_prog_id:
                    if curr_major.std_academic_prog_id.req_curriculum_ids:
                        curr_curriculum = curr_major.std_academic_prog_id.req_curriculum_ids
                        for curriculum in curr_curriculum:
                            if curriculum.course_ids:
                                for course in curriculum.course_ids:
                                    prog_ids.append(course.id)
#                 print '======== Prg', prog_ids
                
                # Get Major Curriculum - All Courses in Major's
                if curr_major.iu_curriculum_ids:
                    for curriculum in curr_major.iu_curriculum_ids:
                        if curriculum.course_ids:
                            for course in curriculum.course_ids:
                                crs_ids.append(course.id)
#                 print '======== Curr', crs_ids
        
            # Starting, incomplete credits = total major credits
            incomplete_creds = record.major_total_credits 
            achieved_creds = 0           
            passing_grade = self.env['ir.config_parameter'].get_param('iuopensys_course.course_passing_grade')
            
            if record.student_course_ids:
                # 1. Retrieve all courses in Curriculum of Major
                # 2. Compare with the current courses -> which one complete
                    # Update incomplete_credits
                    # Update the incomplete course list
                # 3. Remove the course from the list. Display           
            
                crs_ids_copy = crs_ids[:] # make copy of major curriculum
                
                # course_gpa is computed field vs passing_grade ->
                # if there is error, check here
                # Moreover, course must be in Curriculum to be counted
                for student_course in record.student_course_ids:
                    # Only check course that is complete or with passing grade
                    if student_course.is_complete or student_course.course_gpa >= float(passing_grade):
                        
#                         print 'ID ', student_course.offer_course_id.course_id.id, ' ', student_course.offer_course_id.course_id.name
                        
                        if student_course.offer_course_id.course_id.id in crs_ids:
                            crs_ids.remove(student_course.offer_course_id.course_id.id) # -> update Curriculum list
                            
                            complete_crs_ids.append(student_course.offer_course_id.course_id.id)
                        
                        # If not Major courses, check with the Academic Program Courses -> remove if needed
                        if student_course.offer_course_id.course_id.id in prog_ids:
                            prog_ids.remove(student_course.offer_course_id.course_id.id) # -> update IU Program List
                        
                        # Only count Course that has Credit option. P/F option will be ignored
                        # Course that belongs to the curriculum will be counted ->Transferred made
                        if student_course.offer_course_id.course_id.cred_count_type == 'count' and\
                            student_course.offer_course_id.course_id.id in crs_ids_copy:
                            
                            incomplete_creds -= student_course.offer_course_id.course_id.number_credits
                            achieved_creds += student_course.offer_course_id.course_id.number_credits
            
            record.major_course_not_complete_ids = crs_ids
            record.major_course_complete_ids = complete_crs_ids
            record.major_incomplete_credits = incomplete_creds
            record.major_accumulated_credits = achieved_creds 
            record.academic_program_course_not_complete_ids = prog_ids       
                
    
#     @api.model
#     def create(self, vals):
#         curr_student = super(Student, self).create(vals)
        
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
                
                if ('department_id' or 'major_id') in vals:
                    
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
                    if student_logs:
                        for log in student_logs:
                            # Any log with old value is the current changing value in VALS -> Stop
                            if log.old_value == (dept or major):
                                print '++++++ No change Dept/Major.'
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
                        
                        
                        
                        
                        
                        
                        
                   
                   
                    