from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError, Warning

class OfferCourse(models.Model):
    
    _name = 'offer.course'
    _description = 'Offered Course in Semester'
    
    def _default_number_credits_actual(self):
        context = self._context
        if 'default_course_id' in context:
            res = self.env['course'].search([('id','=', context['default_course_id'])])
            if res:
                return res[0].number_credits
        return 0
    
    # Course Info
    name = fields.Char(string='Title')
    course_id = fields.Many2one('course', string='Parent Course', ondelete='cascade')
    prereq_course_id = fields.Many2one(related='course_id.prereq_course_id')
    
    course_type = fields.Selection(related='course_id.course_type')
    crs_lang = fields.Selection(related='course_id.crs_lang')
    
    course_code = fields.Char(string='Course Code', size=10,
                              compute='_generate_course_code')
    course_group = fields.Selection(selection=[('grp1', 'Group 1'),
                                               ('grp2', 'Group 2'),
                                               ('grp3', 'Group 3'),
                                               ('grp4', 'Group 4'),
                                               ('grp5', 'Group 5'),],
                                    string='Group', help='Group of Courses')
    department_id = fields.Many2one('department', string='Department',
                                    related='course_id.department_id',
                                    store=True)
    numb_students = fields.Integer(string='Size',
                                   help='Maximum number of students for each offered course')
    
    # Compute here
    curr_enroll_students = fields.Integer(string='Current Students',
                                        default=0)
    avail_students = fields.Integer(string='Available', compute='_get_avail_students')
    
    assign_room = fields.Char(string='Assigned Room')
    number_credits = fields.Integer('Credits', related='course_id.number_credits')
    number_credits_actual = fields.Integer('Credits for Tuition', required=True,
                                           related="course_id.number_credits_actual")
    dept_academic_code = fields.Char('Department Code', related='department_id.dept_academic_code')
    
    # Notice Lab and PT Theory Class is similar
    lab_sect_display = fields.Boolean('Display Lab Section', default=False)
    has_lab = fields.Boolean(string='Requires Lab', default=False)
    is_lab = fields.Boolean(string='Active Lab')
    lab_type = fields.Selection(selection=[('separate', 'Separate'),
                                           ('combine', 'Combine')],
                                string='Lab Type',
                                help='Determine if the lab is grouped with theory class or is separated')
    theory_course_id = fields.Many2one('offer.course', string='Theory Course')
    lab_course_ids = fields.One2many('offer.course', 'theory_course_id', string='Lab Courses')
        
    # Other Info
    academic_year_id = fields.Many2one('academic.year', string='Class',
                                       domain="[('department_id','=',department_id)]")
    semester_id = fields.Many2one('semester', string='Semester')
    lecturer_id = fields.Many2one('lecturer', string='Instructor')
    
    # Student List
    student_course_ids = fields.One2many('student.course', 'offer_course_id',
                                         string='Students')
    student_attendance_ids = fields.One2many('student.course', 'offer_course_id', string='Attendance')
    
    # Grade and Trancsript
    mid_exam_percent = fields.Float(string='Midterm Exam Percentage')
    final_exam_percent = fields.Float(string='Final Exam Percentage')
    assignment_percent = fields.Float(string='Assignment Percentage')
    
    # PERIOD, EXAM SCHEDULE and TIME SCHEDULE go here
#     calendar_event_ids = fields.One2many('calendar.event', 'offer_course_id', string='Session')
    study_session_ids = fields.One2many('study.period','offer_course_id',string='Periods',
                                        domain=[('is_exam','=',False)])
    exam_session_ids = fields.One2many('study.period', 'offer_course_id', string='Examination',
                                       domain=[('is_exam','=',True)])
    has_exam = fields.Boolean('Has Exam')
    
    # For Attendance Purpose (each sess/week or multiple sessions/week)
    amount_session = fields.Integer('Amt. Sessions', compute='_get_display_details')
    
    display_study_daytime = fields.Text(string='Day(s) and Time(s)', compute='_get_display_details')
    display_course_period = fields.Text(string='Period(s)', compute='_get_display_details')
    display_lecturer = fields.Text(string='Instructor(s)', compute='_get_display_details')
    display_room = fields.Text(string='Room(s)', compute='_get_display_details')
    
    # For Examination Schedule
    display_exam_date_midterm = fields.Text(string='Exam Date', compute='_get_exam_display_details')
    display_exam_time_midterm = fields.Text(string='Start Time', compute='_get_exam_display_details')
    display_duration_midterm = fields.Text(string='Duration', compute='_get_exam_display_details')
    display_room_midterm = fields.Text(string='Room', compute='_get_exam_display_details')
    display_exam_date_final = fields.Text(string='Exam Date', compute='_get_exam_display_details')
    display_exam_time_final = fields.Text(string='Start Time', compute='_get_exam_display_details')
    display_duration_final = fields.Text(string='Duration', compute='_get_exam_display_details')
    display_room_final = fields.Text(string='Room', compute='_get_exam_display_details')
    
    # Tuition - is separate for each of the courses
    tuition_id = fields.Many2one('course.tuition', string='Credit Cost',
                                 default=lambda self:self.env['course.tuition'].search([('id','=',1)]))
    
    crs_tuition = fields.Float('Cost', compute='_get_course_tuition')
    
    # Note
    ext_note = fields.Text('Note')
    
    @api.onchange('exam_session_ids')
    def onchange_exam_session_ids(self):
        if self.exam_session_ids:
            if not self.has_exam:
                self.has_exam = True
        else:
            self.has_exam = False
                    
    @api.multi
    def print_exam_student_list(self):
        report_name = 'iuopensys_course.report_exam_student_list'
        return self.env['report'].get_action(self, report_name)
    
    @api.multi
    def print_student_attendance_check(self):
        report_name = 'iuopensys_course.report_student_attendance_check'
        return self.env['report'].get_action(self, report_name)
    
    @api.constrains('mid_exam_percent','final_exam_percent','assignment_percent')
    def _validate_grade_percent(self):
        for record in self:
            temp = record.mid_exam_percent + record.final_exam_percent + record.assignment_percent
            if temp > 1 or temp < 0:
                raise ValidationError('Please check Grade Distribution.')
    
    @api.constrains('study_session_ids')
    def _check_overlap_study_session(self):
        for record in self:
            if record.study_session_ids:
                session_lst = []
                for session in record.study_session_ids:
                    # Temp ('Char', float, float)
                    temp = (session.crs_day, session.start_time, session.end_time)
                    if not any(session.crs_day in item for item in session_lst):
                        session_lst.append(temp)
                    else:
                        temp_lst = [(item[1],item[2]) for item in session_lst if item[0] == session.crs_day]
                        temp_lst.append((session.start_time, session.end_time))
#                         print '+++++', temp_lst
                        overlap_res = [[x,y] for x in temp_lst for y in temp_lst if x is not y and x[1] >= y[0] and x[0] <= y[0]]
                        if len(overlap_res) > 0:
                            raise ValidationError('Each session\'s date & time must be different.')
                        
    @api.depends('tuition_id', 'number_credits')
    def _get_course_tuition(self):
        for record in self:
#             if record.is_lab and record.lab_type == 'combine':
#                 record.crs_tuition = 0.0
#             else:
            record.crs_tuition = (record.tuition_id.credit_cost * record.number_credits_actual) or 0.0                             
                                          
    @api.multi
    def name_get(self):
        res = super(OfferCourse,self).name_get()
        data = []
        
        for record in self:
            val = ''
            val += record.course_code or ""
            val += ' - ' + record.name
            data.append((record.id, val))
        return data
    
    @api.onchange('course_id','theory_course_id')
    def _onchange_course_id(self):
        if self.course_id or self.theory_course_id:
            self.name = self.course_id.name or self.theory_course_id.name
        # For Lab course only
#         if self.is_lab and self.theory_course_id:
#             if not self.course_id:
#                 self.course_id = self.theory_course_id.course_id
#             if not self.academic_year_id:
#                 self.academic_year_id = self.theory_course_id.academic_year_id
#             if not self.semester_id:
#                 self.semester_id = self.theory_course_id.semester_id
        if self.is_lab:
            self.course_id = self.theory_course_id.course_id
            self.academic_year_id = self.theory_course_id.academic_year_id
            self.semester_id = self.theory_course_id.semester_id               
    
    # Unique Course Code
    def _generate_str_id(self, id):
        if id >= 1 and id <= 9:
            return '00' + str(id)
        elif id >= 10 and id <= 99:
            return '0' + str(id)
        else:
            return str(id)
        
    @api.multi
    def _generate_course_code(self):
        for record in self:
            record.course_code = record.department_id.dept_academic_code +\
                                 record._generate_str_id(record.id) + 'IU'
    
    @api.depends('numb_students', 'student_course_ids')
    def _get_avail_students(self):
        for record in self:
            if record.student_course_ids:
                record.avail_students = record.numb_students - len(record.student_course_ids)
            else:
                record.avail_students = record.numb_students
                                
    @api.depends('theory_course_id','study_session_ids')
    def _get_display_details(self):     
        for record in self:
            temp = ''
            temp_lect = ''
            temp_room = ''
            temp_date = ''
            day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # Lab course record
            if record.is_lab: 
                # Get Theory days first
                if record.theory_course_id:                    
                    temp = record.theory_course_id.display_study_daytime or ''
                    temp_lect = record.theory_course_id.display_lecturer or ''
                    temp_room = record.theory_course_id.display_room or '' 
                    temp_date = record.theory_course_id.display_course_period or ' '                      
                # Get Lab days        
                if record.study_session_ids:
                    # For amount of session
                    amt_session = 0
                    for session in record.study_session_ids:
                        start_d = datetime.strptime(session.start_date, '%Y-%m-%d')
                        end_d = datetime.strptime(session.end_date, '%Y-%m-%d')
                        
                        weeks = ((end_d - start_d).days)/7
                        # In case only 1 section - same day
                        if weeks == 0:
                            weeks = 1
                        amt_session += weeks
                        
                        end_d = datetime.strftime(end_d, '%d/%m/%y')
                        temp_date += datetime.strftime(start_d,'%d/%m/%y')
                        temp_date += ' - ' + end_d + ' [**]\n'                      
                        day_indx = start_d.weekday()
                        temp += day[day_indx] + '\t| '
                        start_t = session._get_time(session.start_time)
                        end_t = session._get_time(session.end_time)
                        temp += start_t + '-' + end_t + ' [**]' +'\n'
                                            
                    record.amount_session = amt_session
                                            
                if record.lecturer_id:
                    temp_lect += (record.lecturer_id.name + '\n') or ''
                if record.assign_room:
                    temp_room += (record.assign_room + '\n') or ''
                
            # Lecture Course record
            else:         
                if record.study_session_ids:
                    amt_session = 0
                    for session in record.study_session_ids:
                        start_d = datetime.strptime(session.start_date, '%Y-%m-%d')
                        end_d = datetime.strptime(session.end_date, '%Y-%m-%d')
                        
                        weeks = ((end_d - start_d).days)/7
                        # In case only 1 section - same day
                        if weeks == 0:
                            weeks = 1
                        amt_session += weeks
                        
                        end_d = datetime.strftime(end_d, '%d/%m/%y')
                        temp_date += datetime.strftime(start_d,'%d/%m/%y')
                        temp_date += ' - ' + end_d + '\n'                      
                        day_indx = start_d.weekday()
                        temp += day[day_indx] + '\t| '
                        start_t = session._get_time(session.start_time)
                        end_t = session._get_time(session.end_time)
                        temp += start_t + '-' + end_t + '\n'
#                     if len(record.study_session_ids):
#                         temp += '\n'

                    record.amount_session = amt_session

                if record.lecturer_id:
                    temp_lect = record.lecturer_id.name + '\n\n'
                if record.assign_room:
                    temp_room = record.assign_room + '\n\n'
                    
            record.display_study_daytime = temp or ''
            record.display_lecturer = temp_lect or ''
            record.display_room = temp_room or ''
            record.display_course_period = temp_date or ''
            
    @api.depends('exam_session_ids')
    def _get_exam_display_details(self):
        for record in self:
            if record.exam_session_ids:
                for session in record.exam_session_ids:
                    temp_date = ''
                    temp_time = ''
                    temp_room = ''
                    temp_duration = ''
                    start_d = datetime.strptime(session.start_date, '%Y-%m-%d')
                    temp_date += datetime.strftime(start_d,'%d/%m/%y')
                    start_t = session._get_time(session.start_time)
                    temp_time += start_t
                    duration = session._get_time(session.duration)
                    temp_duration += duration
                    temp_room += session.exam_room or ''
                    if session.exam_type == 'mid':
                        record.display_exam_date_midterm = temp_date or ''
                        record.display_exam_time_midterm = temp_time or ''
                        record.display_duration_midterm = temp_duration or ''
                        record.display_room_midterm = temp_room or ''
                    elif session.exam_type == 'final':
                        record.display_exam_date_final = temp_date or ''
                        record.display_exam_time_final = temp_time or ''
                        record.display_duration_final = temp_duration or ''
                        record.display_room_final = temp_room or ''
                        
    @api.multi
    def write(self, vals):
        for record in self:
            if 'student_course_ids' in vals:
                old_ids = [a.id for a in record.student_course_ids]
                ids = [b[1] for b in vals['student_course_ids'] if b[0] == 2]
                
                not_remove_ids = [c for c in vals['student_course_ids'] if c[0] != 2]
                                
                # Since create has been disable -> only opt delete is used
                # So different ids here are the deleted ones
                student_ids = []
                for student_course in record.student_course_ids:
                    if student_course.id in ids:
                        student_ids.append(student_course.student_id.id)
                
                remove_student_ids = self.env['student'].search([('id','in',student_ids)])
                if remove_student_ids:
                    # Remove each crs registration for student
                    for student in remove_student_ids:
                        std_reg_id = self.env['student.registration'].search([('student_id','=',student.id),
                                                                              ('semester_id','=',record.semester_id.id)])
                        if std_reg_id:
                            offer_crs_ids = std_reg_id.offer_course_ids.ids
                            # Loop through each course in registration form
                            # If found a course that match with the record.id
                            # or course that in record.lab_course_ids
                            # Remove course from the registration
                            for offer_course in std_reg_id.offer_course_ids:
#                                 if record.has_lab:
#                                     if offer_course.id in record.lab_course_ids.ids:
                                if offer_course.id == record.id or\
                                    offer_course.id in record.lab_course_ids.ids:
                                    offer_crs_ids.remove(offer_course.id)
                            
                            new_vals = {'offer_course_ids': [(6,0,offer_crs_ids)]}
                            std_reg_id.write(new_vals)
                            
                vals['student_course_ids'] = not_remove_ids # To avoid scenario when removing_ids cant be found 
                # since std_regstration have removed it first
        
        return super(OfferCourse,self).write(vals)
                            
            
#     @api.multi
#     def call_student_course_addition_wizard(self):
#         for record in self:
#             wizard_form = self.env.ref('iuopensys_course.student_course_addition_wizard_form_view', False)
#             view_id = self.env['student.course.addition.wizard']
#             vals={'name':'Add Student Wizard'}
#             new = view_id.create(vals)
#             return{
#                    'name': 'Add Students',
#                    'type': 'ir.actions.act_window',
#                    'res_model': 'student.course.addition.wizard',
#                    'res_id': new.id,
#                    'view_id': wizard_form.id,
#                    'view_type': 'form',
#                    'view_mode': 'form',
#                    'context': {'offer_course_id': record.id},
#                    'target': 'new',
#                    }
#                                  
#     @api.model
#     def create(self, vals):
#         """
#         1. When course is created, it will be assigned with study schedule
#         2. After schedule is assigned, the module will automatically
#         create calendar event that fit the schedule.
#         """
#         curr_course = super(OfferCourse, self).create(vals)
#         print '+++++++', curr_course.study_period_ids
#         if curr_course.study_period_ids:
#             for session in curr_course.study_period_ids:
#                 event_name = curr_course.name + '-' + session.name
#                 print '------', session.start_date, ' ', session.start_datetime
#                 new_vals = {'name': event_name,
#                             'start_datetime': session.start_datetime,
#                             'start': session.start_datetime,
#                             'stop': session.end_datetime,
#                             'duration': session.duration,                                          
#                             }
#                 print '+++++', new_vals
# #                 self.env['calendar.event'].create(new_vals)
#         return curr_course
        
        