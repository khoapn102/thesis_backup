from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class OfferCourse(models.Model):
    
    _name = 'offer.course'
    _description = 'Offered Course in Semester'
    
    # Course Info
    name = fields.Char(string='Course Name')
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
    numb_students = fields.Integer(string='Number of Students',
                                   help='Maximum number of students for each offered course')
    # Compute here
    curr_enroll_students = fields.Integer(string='Current Students',
                                        default=0)
    
    assign_room = fields.Char(string='Assigned Room')
    number_credits = fields.Integer('Credits', related='course_id.number_credits')
    dept_academic_code = fields.Char('Department', related='department_id.dept_academic_code')
    # Notice Lab and PT Theory Class is similar
    has_lab = fields.Boolean(string='Requires Lab', default=False)
    is_lab = fields.Boolean(string='Active Lab')
    lab_type = fields.Selection(selection=[('separate', 'Separate'),
                                           ('combine', 'Combine')],
                                string='Lab Type',
                                help='Determine if the lab is grouped with theory class or is separated')
    academic_year_id = fields.Many2one('academic.year', string='Class')
    semester_id = fields.Many2one('semester', string='Semester')
    lecturer_id = fields.Many2one('lecturer', string='Lecturer')
    
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
    
    # If the course is lab, other attributes will be changed
    @api.onchange('is_lab')
    def _onchange_is_lab(self):
        if self.is_lab:
            self.name += ' Lab'
        else:
            self.name = self.course_id.name            
    
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
        
        