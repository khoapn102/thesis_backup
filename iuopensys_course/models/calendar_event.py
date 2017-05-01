from openerp import models, fields, api

class CalendarEvent(models.Model):
    
    _inherit = 'calendar.event'
    
    study_period_id = fields.Many2one('study.period', string='Study Period', ondelete='cascade')
    offer_course_id = fields.Many2one('offer.course',string='Course', related='study_period_id.offer_course_id')
    
    is_planned_event = fields.Boolean('Planned Event')
    
    # TEST EXAM PERIOD - in calendar event 
    # For e.g Exam period is different between class of students
    # Student K13 takes exam weeks 1 week after Student K14 for example
    year_batch_ids = fields.Many2many('year.batch', string='Apply For', 
                                       help='Event is prioritized for these classes of student only.')
    
    # Student Attendance 
#     student_attendance_ids = fields.Many2many('student', string='Attendance')
#     amount_std_total = fields.Integer('Total Students', compute='get_amount_std_attend')
#     amount_std_attend = fields.Integer('Attended', compute='get_amount_std_attend')
#      
#     @api.depends('student_attendance_ids')
#     def get_amount_std_attend(self):
#         for record in self:
#             total = 0
#             attended = 0
#             if record.student_attendance_ids:
#                 for student in record.student_attendance_ids:
#                     total += 1
#                     if student.is_attend:
#                         attended += 1
#             record.amount_std_total = total
#             record.amount_std_attend = attended
    
#     @api.onchange('offer_course_id')
#     def _onchange_offer_course_id(self):
#         for record in self:
#             if record.offer_course_id:
#                 record.name = record.offer_course_id.name + ' - ' + record.session_name

    