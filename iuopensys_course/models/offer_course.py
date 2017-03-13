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
    
    # Grade and Trancsript
    mid_exam_percent = fields.Integer(string='Midterm Exam Percentage', default=0)
    final_exam_percent = fields.Integer(string='Final Exam Percentage', default=0)
    
    # PERIOD, EXAM SCHEDULE and TIME SCHEDULE go here
#     calendar_event_ids = fields.One2many('calendar.event', 'offer_course_id', string='Session')
    study_session_ids = fields.One2many('study.period','offer_course_id',string='Periods',
                                        domain=[('is_exam','=',False)])
    exam_session_ids = fields.One2many('study.period', 'offer_course_id', string='Examination',
                                       domain=[('is_exam','=',True)])
    
    display_study_daytime = fields.Text(string='Day(s) and Time(s)', compute='_get_display_details')
    display_course_period = fields.Text(string='Period(s)', compute='_get_display_details')
    display_lecturer = fields.Text(string='Instructor(s)', compute='_get_display_details')
    display_room = fields.Text(string='Room(s)', compute='_get_display_details')
    
    # Tuition
    tuition_id = fields.Many2one('course.tuition', string='Credit Cost',
                                 related='course_id.tuition_id')
    
    crs_tuition = fields.Float('Cost', compute='_get_course_tuition')
    
    # Note
    ext_note = fields.Text('Note')
    
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
                    for session in record.study_session_ids:
                        start_d = datetime.strptime(session.start_date, '%Y-%m-%d')
                        end_d = datetime.strptime(session.end_date, '%Y-%m-%d')
                        end_d = datetime.strftime(end_d, '%d/%m/%y')
                        temp_date += datetime.strftime(start_d,'%d/%m/%y')
                        temp_date += ' - ' + end_d + ' [**]\n'                      
                        day_indx = start_d.weekday()
                        temp += day[day_indx] + '\t| '
                        start_t = session._get_time(session.start_time)
                        end_t = session._get_time(session.end_time)
                        temp += start_t + '-' + end_t + ' [**]' +'\n'                    
                if record.lecturer_id:
                    temp_lect += (record.lecturer_id.name + '\n') or ''
                if record.assign_room:
                    temp_room += (record.assign_room + '\n') or ''
                
            # Lecture Course record
            else:         
                if record.study_session_ids:
                    for session in record.study_session_ids:
                        start_d = datetime.strptime(session.start_date, '%Y-%m-%d')
                        end_d = datetime.strptime(session.end_date, '%Y-%m-%d')
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
                if record.lecturer_id:
                    temp_lect = record.lecturer_id.name + '\n\n'
                if record.assign_room:
                    temp_room = record.assign_room + '\n\n'
                    
            record.display_study_daytime = temp or ''
            record.display_lecturer = temp_lect or ''
            record.display_room = temp_room or ''
            record.display_course_period = temp_date or ''
                                 
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
        
        