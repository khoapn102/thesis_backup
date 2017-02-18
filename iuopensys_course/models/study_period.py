from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import pytz
from pytz import timezone

class StudyPeriod(models.Model):
    
    _name = 'study.period'
    _description = 'Study Period for Course (Session, Examination, etc.)'
    
    name = fields.Char('Event Name', size=16, required=True,
                       default="Teaching 1")
    offer_course_id = fields.Many2one('offer.course', string='Course', ondelete='cascade')
    start_date = fields.Date(string='Start Date',
                                    default = datetime.now().strftime("%Y-%m-%d"),
                                    help='Period start date')
    end_date = fields.Date(string='End Date',
                                  default=datetime.now() + relativedelta(days=102),
                                  help='Period end date')
    start_time = fields.Float(string='Start at (24h)', required=True,
                              help='Session start time (24h)')
    end_time = fields.Float(string='End at (24h)', required=True,
                            help='Session end time')
    duration = fields.Float('Duration', required=True)
    is_summer = fields.Boolean(string='Summer Session')
    is_exam = fields.Boolean(string='Exam Session', default=False)
    exam_type = fields.Selection(selection=[('mid','Midterm'),
                                            ('final','Final')],
                                 string='Exam Type', default='mid')
#     start_datetime = fields.Datetime('Start Session (same day)')
#     end_datetime = fields.Datetime('End Session (same day)')
    
    @api.constrains('start_time','end_time')
    def _check_start_end_time(self):
        for record in self:
            if record.duration <= 0:
                raise ValidationError('End time must be greater than Start time !')            
        
    def _get_time(self, time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(time * 60, 60))
    
    def _get_datetime(self, date, time):
        if self._context is None:
            self._context = {}
        
        print self._context
        local = pytz.timezone(self._context.get('tz') or 'Asia/Saigon')        
        
        time_res = '{0:02.0f}:{1:02.0f}:00'.format(*divmod(time * 60, 60))
        temp_res = str(date) + ' ' + time_res
        my_dt = datetime.strptime(temp_res, '%Y-%m-%d %H:%M:%S')
        
        loc_dt = local.localize(my_dt, is_dst=None)
        utc_dt = loc_dt.astimezone(pytz.utc)
#         print '++++++', utc_dt 
        return utc_dt.strftime('%Y-%m-%d %H:%M:%S')
         
    @api.onchange('start_time','end_time')
    def _onchange_start_end_time(self):
        self.duration = self.end_time - self.start_time
        
    @api.onchange('is_exam','exam_type')
    def _onchange_is_exam(self):
        if self.is_exam:
            if self.exam_type == 'mid':
                self.name = 'Midterm Exam'
            elif self.exam_type == 'final':
                self.name = 'Final Exam'
    
    @api.model
    def create(self, vals):
        curr_period = super(StudyPeriod,self).create(vals)
#         print '-------', self._context   
        start_dt = curr_period._get_datetime(curr_period.start_date, curr_period.start_time)
        end_dt = curr_period._get_datetime(curr_period.start_date, curr_period.end_time)
        event_name = curr_period.offer_course_id.name + '-' + curr_period.name
        new_vals = {'name': event_name,
                    'start_datetime': start_dt,
                    'start': start_dt,
                    'stop': end_dt,
                    'duration': curr_period.duration,
                    'study_period_id': curr_period.id,                                          
                    }
#         print '+++++', new_vals
        self.env['calendar.event'].create(new_vals)
        return curr_period
            