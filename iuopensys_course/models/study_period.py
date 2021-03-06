from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import pytz
from pytz import timezone

class StudyPeriod(models.Model):
    
    # Default value
    def _get_default_period_start_morning(self):
        return self.env['ir.config_parameter'].get_param('iuopensys_course.time_start_morning')
    def _get_default_period_length(self):
        return self.env['ir.config_parameter'].get_param('iuopensys_course.period_length')
    def _get_default_period_start_afternoon(self):
        return self.env['ir.config_parameter'].get_param('iuopensys_course.time_start_afternoon')
    
    period_time_start = {'1': 8.0, '2': 8.75, '3': 10, '4': 10.75, '5': 11.5,
                         '6': 13.0, '7': 13.75, '8': 14.75, '9':15.5, '10': 16.25}
    period_time_end = {'1': 8.75, '2': 9.5, '3': 10.75, '4': 11.5, '5': 12.25,
                       '6': 13.75, '7': 14.5, '8': 15.5, '9': 16.25, '10': 17.0}
    period_dur = ['1','2','3','4','5','6','7', '8', '9', '10']
    
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
    crs_day = fields.Char(string='Start Day', compute='_get_course_day')
    
    is_recurrency = fields.Boolean(string='Recurrent Session', default=True)
    
    time_start_morning = fields.Float('Period Start time',
                                        default=_get_default_period_start_morning)
    time_start_afternoon = fields.Float('Period Start time', 
                                        default=_get_default_period_start_afternoon)
    default_period_length = fields.Float('Period Length time',
                                         default=_get_default_period_length)
    
    study_period_start = fields.Selection(selection=[('1', 'Period 1'),
                                                     ('2', 'Period 2'),
                                                     ('3', 'Period 3'),
                                                     ('4', 'Period 4'),
                                                     ('5', 'Period 5'),
                                                     ('6', 'Period 6'),
                                                     ('7', 'Period 7'),
                                                     ('8', 'Period 8'),
                                                     ('9', 'Period 9'),
                                                     ('10', 'Period 10')], string='Start Period')
    amount_period = fields.Selection(selection=[('1', '1'),
                                                ('2', '2'),
                                                ('3', '3'),
                                                ('4', '4'),
                                                ('5', '5')],
                                     string='Amt', help='Amount periods for session')

    
#     start_datetime = fields.Datetime('Start Session (same day)')
#     end_datetime = fields.Datetime('End Session (same day)')
    @api.constrains('start_date', 'end_date')
    def _validate_study_period(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
    
    @api.depends('start_date')
    def _get_course_day(self):
        day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for record in self:
            indx = datetime.strptime(record.start_date, '%Y-%m-%d').weekday()
            record.crs_day = day[indx]
    
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
    
    @api.onchange('study_period_start', 'amount_period')
    def _onchange_study_period(self):        
        print '++++', float(self.time_start_morning), ' ', self.default_period_length, ' ', self.time_start_afternoon
        if self.study_period_start:
            self.start_time = self.period_time_start[self.study_period_start]
#             if int(self.study_period_start) <= 5:
#                 self.start_time = float(self.time_start_morning) + (int(self.study_period_start)-1)*float(self.default_period_length)
#             else:
#                 self.start_time = float(self.time_start_afternoon) + (int(self.study_period_start)-6)*float(self.default_period_length)
        if self.amount_period:
            index = str(int(self.study_period_start) + int(self.amount_period) - 1)
#             self.end_time = self.start_time + int(self.amount_period)*self.default_period_length
            self.end_time = self.period_time_end[index]
    
    @api.model
    def create(self, vals):
        curr_period = super(StudyPeriod,self).create(vals)
#         print '-------', self._context   
        lecturer_id = curr_period.offer_course_id.lecturer_id
        start_dt = curr_period._get_datetime(curr_period.start_date, curr_period.start_time)
        end_dt = curr_period._get_datetime(curr_period.start_date, curr_period.end_time)
        lab = ''
        if curr_period.offer_course_id.is_lab:
            lab = ' Lab '
        else:
            lab = ' '
        event_name = curr_period.offer_course_id.name + lab +\
                     curr_period.offer_course_id.course_code + '-' + curr_period.name
        new_vals = {'name': event_name,
                    'start_datetime': start_dt,
                    'start': start_dt,
                    'stop': end_dt,
                    'duration': curr_period.duration,
                    'study_period_id': curr_period.id,
                    'partner_ids': [(6, 0, [lecturer_id.user_id.partner_id.id])],                                         
                    }
        if curr_period.is_recurrency:
            new_vals['recurrency'] = True
            new_vals['interval'] = 1
            new_vals['rrule_type'] = 'weekly'
            new_vals['end_type'] = 'end_date'
            new_vals['final_date'] = curr_period.end_date
#         print '+++++', new_vals
        self.env['calendar.event'].create(new_vals)
        return curr_period
    
    @api.multi
    def write(self, vals):
        """
        1. If any date/time change
        2. Save the list of partner. Then delete all prev events.
        3. Create new events base on the new date/time with prev partner list.
        """
        for record in self:
            if vals:
                event_ids = self.env['calendar.event'].search([('study_period_id', '=', record.id)])
                partner_ids = event_ids[0].partner_ids
                lst_partner = []
                for partner in partner_ids:
                    lst_partner.append(partner.id)
                event_ids.unlink()
                lecturer_id = record.offer_course_id.lecturer_id
                rec_start_dt = vals['start_date'] if 'start_date' in vals else record.start_date
                rec_end_dt = vals['end_date'] if 'end_date' in vals else record.end_date
                rec_start_time = vals['start_time'] if 'start_time' in vals else record.start_time
                rec_end_time = vals['end_time'] if 'end_time' in vals else record.end_time
                duration = vals['duration'] if 'duration' in vals else record.duration
                # If the course is Lab add Lab into its event's name
                lab = ''
                if record.offer_course_id.is_lab:
                    lab = ' Lab '
                else:
                    lab = ' '
                start_dt = record._get_datetime(rec_start_dt, rec_start_time)
                end_dt = record._get_datetime(rec_start_dt, rec_end_time)
                event_name = record.offer_course_id.name + lab +\
                     record.offer_course_id.course_code + '-' + record.name
                new_vals = {'name': event_name,
                            'start_datetime': start_dt,
                            'start': start_dt,
                            'stop': end_dt,
                            'duration': duration,
                            'study_period_id': record.id,
                            'partner_ids': [(6, 0, lst_partner)],                                          
                            }
                if record.is_recurrency:
                    new_vals['recurrency'] = True
                    new_vals['interval'] = 1
                    new_vals['rrule_type'] = 'weekly'
                    new_vals['end_type'] = 'end_date'
                    new_vals['final_date'] = rec_end_dt
                self.env['calendar.event'].create(new_vals)
        return super(StudyPeriod,self).write(vals)
                    
                
    
            