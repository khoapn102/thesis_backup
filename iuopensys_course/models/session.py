from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

class Session(models.Model):
    
    _name = 'session'
    _description = 'Course Session'
    
    name = fields.Char('Session Name', size=16, required=True,
                       default="Session 1")
    offer_course_id = fields.Many2one('offer.course', string='Course', ondelete='cascade', required=True)
    start_date = fields.Date(string='Start Date',
                                    default = datetime.now().strftime("%Y-%m-%d"))
    end_date = fields.Date(string='End Date',
                                  default=datetime.now() + relativedelta(days=102))
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    duration = fields.Float('Duration', required=True)
    is_summer = fields.Boolean(string='Summer Session')
    
    
    def _get_datetime(self, date, time):
        time_res = '{0:02.0f}:{1:02.0f}:00'.format(*divmod(time * 60, 60))
        print '+++++', date
        temp_res = str(date) + ' ' + time_res
        res = datetime.strptime(temp_res, '%Y-%m-%d %H:%M:%S')
        print '++++++', res 
        return res.strftime('%Y-%m-%d %H:%M:%S')

#     @api.onchange('start_time')
#     def _onchange_start_time(self):
#         print '-------', self.temp
#         self.temp = self._get_datetime(self.start_date, self.start_time)
        
    @api.onchange('end_time')
    def _onchange_start_end_time(self):
        self.duration = self.end_time - self.start_time
        
    @api.constrains('start_time','end_time')
    def _check_start_end_time(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError('End time must be greater than Start time !')
            
#     @api.model
#     def create(self, vals):
#         curr_session = super(Session,self).create(vals)
#         start_datetime = self._get_datetime(curr_session.start_date,curr_session.start_time)
#         end_datetime = self._get_datetime(curr_session.end_date,curr_session.end_time)
#         new_vals = {'name': curr_session.offer_course_id.name,
#                     'start_datetime': start_datetime,
#                     'duration': curr_session.duration,                        
#                     }
#         print '+++++', new_vals
#         self.env['calendar.event'].create(new_vals)
#         return curr_session
        
#     display_hour = fields.Char(string='Recording Hour',
#                                 compute='_get_display_hour')
#     display_duration = fields.Char(string='Recording Duration',
#                                    compute='_get_display_duration')
#     
#     @api.multi
#     def _get_display_hour(self):
#         for record in self:
#             record.display_hour = record.hour + ':' + record.minute
#             