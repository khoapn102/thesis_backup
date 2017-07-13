from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
import pytz
from pytz import timezone

def get_date_from_event_id(event_id):
    tmp_str = event_id.split('-')[1]
    tmp_date = tmp_str[:8]
    print '------', tmp_date
    date_str = tmp_date[:4] + '-' + tmp_date[4:6] + '-' + tmp_date[6:8]
    return date_str

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
    
    proctor_one_id = fields.Many2one('lecturer', string='First Proctor')
    proctor_two_id = fields.Many2one('lecturer', string='Second Proctor')
    
    exam_type = fields.Selection(selection=[('mid','Midterm'),
                                            ('final','Final'),
                                            ('other','Other')],
                                 string='Exam Type', default='mid')
    
    exam_room = fields.Char('Exam Room')
    
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
    
    # For case the session is on 1 day only. No recurrency is needed
    @api.onchange('is_recurrency')
    def onchange_is_recurrency(self):
        if not self.is_recurrency:
            self.end_date = self.start_date            
    
    @api.constrains('start_date', 'end_date')
    def _validate_study_period(self):
        # Validate field for Course time. Exam must not checked this validation
        for record in self:
            if not record.is_exam:
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
            elif self.exam_type == 'other':
                self.name = 'Exam'
    
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
    
    @api.onchange('start_date','is_exam')
    def _onchange_start_date(self):
        if self.is_exam:
            self.end_date = self.start_date
    
    @api.model
    def create(self, vals):
        # Every time it created, it will create calendar.event
        # Then add the corresponding users.
               
        curr_period = super(StudyPeriod,self).create(vals)
        
        # 1. Check if This is EXAM SESSION ?
        # If current study_period is exam -> check student
        # Then create the calendar event        
        if curr_period.is_exam:            
            lst_partner = [3,] # List of partner            
            if curr_period.proctor_one_id:
                lst_partner.append(curr_period.proctor_one_id.user_id.partner_id.id)
            if curr_period.proctor_two_id:
                lst_partner.append(curr_period.proctor_two_id.user_id.partner_id.id)
                
            # Check Student list who has been paid (atm check pay in full/not)
            std_crs_ids = self.env['student.course'].search([('offer_course_id','=',curr_period.offer_course_id.id)])
            # Retrieve Student-course entity (all students of the course)
            for std_crs in std_crs_ids:
                student = self.env['student'].search([('id','=',std_crs.student_id.id)])
                if student:
                    lst_partner.append(student.user_id.partner_id.id)
                    if student.student_debt > 0:
                    # If student havent paid (exam_status is global here set need to set only once), 
                    # -> set exam_status to False at once (for all courses)
                        if student.exam_status:
                            student.write({'exam_status':False})
            
            event_name =  curr_period.offer_course_id.name + ' ' + curr_period.offer_course_id.course_code +\
                            '-' + curr_period.name  
            start_dt = curr_period._get_datetime(curr_period.start_date, curr_period.start_time)
            end_dt = curr_period._get_datetime(curr_period.start_date, curr_period.end_time)
            new_vals = {'name': event_name,
                        'start_datetime': start_dt,
                        'start': start_dt,
                        'stop': end_dt,
                        'duration': curr_period.duration,
                        'study_period_id': curr_period.id,
                        'partner_ids': [(6,0, lst_partner)]                   
                        }
            self.env['calendar.event'].create(new_vals)
        
        # 2. STUDY SESSIONS - Course schedule, etc.
        else:      
#         print '-------', self._context
            
            # Add Lecturer to the schedule 
            lecturer_id = curr_period.offer_course_id.lecturer_id or False
            start_dt = curr_period._get_datetime(curr_period.start_date, curr_period.start_time)
            end_dt = curr_period._get_datetime(curr_period.start_date, curr_period.end_time)
            lab = ''
            # For Lab Course
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
                        }
            if lecturer_id:
                new_vals['partner_ids'] = [(6, 0, [lecturer_id.user_id.partner_id.id, 3])]
            else:
                # 3 is Administrator as default partner
                new_vals['partner_ids'] = [(6, 0, [3])]
                
            if curr_period.is_recurrency:
                new_vals['recurrency'] = True
                new_vals['interval'] = 1
                new_vals['rrule_type'] = 'weekly'
                new_vals['end_type'] = 'end_date'
                new_vals['final_date'] = curr_period.end_date
    #         print '+++++', new_vals
            self.env['calendar.event'].create(new_vals)
            planned_ids = self.env['calendar.event'].search([('is_planned_event','=', True),
                                                             ('start_date', '>=', curr_period.start_date),
                                                             ('start_date', '<=', curr_period.end_date)])
            print '++++ Planned', planned_ids
            planned_dates = [(p_event.start_date, p_event.stop_date) for p_event in planned_ids]
            print '------ Holiday', planned_dates
            # For each planned date, find the session that overlap with this. -> delete those sessions
            # Also must check if the Exam period is fit for Which Student Academic year
            if planned_ids:
    #             print '===== HoLIDAy', planned_dates
                for p_event in planned_ids:
                    # Planned event only apply for certain student batches
                    # Check if the current course' student batch is in the Event's 
                    # If course's year batch not in the event's batch list, -> skip this event.
                    if p_event.year_batch_ids:
                        if curr_period.offer_course_id.academic_year_id.year_batch_id.id not in p_event.year_batch_ids.ids:
                            continue
                        
                    study_session_ids = self.env['calendar.event'].search([('study_period_id','=', curr_period.id),])
    #                 print '======= Sessions', study_session_ids                    
                    for session in study_session_ids:
                        
                        # Recurring events will have the date in the name
                        if session.recurrency:
                                    session_date = get_date_from_event_id(session.id)
                        else: # Otherwise only 1 date, get the start_date
                            session_date = session.start_date 
                                  
                        session_date = get_date_from_event_id(session.id)
                        # Non-recurring event will have the date save in data
                        if p_event.start_date <= session_date <= p_event.stop_date:
    #                         print 'Delete ----', session.id
                            session.unlink() 
    #                 study_session_ids.unlink()
        return curr_period
    
    @api.multi
    def write(self, vals):
        """
        1. If any date/time change
        2. Save the list of partner. Then delete all prev events.
        3. Create new events base on the new date/time with prev partner list.
        4. Check for Holidays/Planned Event to apply new changes.
        """
        for record in self:
            # Check if any changes in current study_period
            if vals:
                event_ids = self.env['calendar.event'].search([('study_period_id', '=', record.id)])
                partner_ids = event_ids[0].partner_ids
                lst_partner = []
                # Retrieve current partner
                for partner in partner_ids:
                    lst_partner.append(partner.id) # Reuse the partner list (include lecturer already)
                event_ids.unlink() # Clear all calendar_event ids                
                    
                # Get Lecturer of current Course
                lecturer_id = record.offer_course_id.lecturer_id
                
                rec_start_dt = vals['start_date'] if 'start_date' in vals else record.start_date
                rec_end_dt = vals['end_date'] if 'end_date' in vals else record.end_date
                rec_start_time = vals['start_time'] if 'start_time' in vals else record.start_time
                rec_end_time = vals['end_time'] if 'end_time' in vals else record.end_time
                duration = vals['duration'] if 'duration' in vals else record.duration
                
                new_vals = {}
                
                # Exam Period
                if record.is_exam:
                    event_name = record.offer_course_id.name + ' ' +\
                                 record.offer_course_id.course_code +\
                                 '-' + record.name
                            
                    # Update new proctors     
                    if 'proctor_one_id' in vals:
                        if record.proctor_one_id:
                            lst_partner.remove(record.proctor_one_id.user_id.partner_id.id)
                            proctor_id = self.env['lecturer'].search([('id','=',vals['proctor_one_id'])])
                            lst_partner.append(proctor_id.user_id.partner_id.id)
                            
                    if 'proctor_two_id' in vals:
                        if record.proctor_two_id:
                            lst_partner.remove(record.proctor_two_id.user_id.partner_id.id)
                            proctor_id = self.env['lecturer'].search([('id','=',vals['proctor_two_id'])])
                            lst_partner.append(proctor_id.user_id.partner_id.id)
                        
                    start_dt = record._get_datetime(rec_start_dt, rec_start_time)
                    end_dt = record._get_datetime(rec_start_dt, rec_end_time)
                    new_vals = {'name': event_name,
                        'start_datetime': start_dt,
                        'start': start_dt,
                        'stop': end_dt,
                        'duration': record.duration,
                        'study_period_id': record.id,
                        'partner_ids': [(6,0, lst_partner)]                   
                        }
                    self.env['calendar.event'].create(new_vals)
                # Not exam, study session/other
                else:
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
                    planned_ids = self.env['calendar.event'].search([('is_planned_event','=', True),
                                                             ('start_date', '>=', record.start_date),
                                                             ('start_date', '<=', record.end_date)])
                    print '++++ Planned', planned_ids
                    planned_dates = [(p_event.start_date, p_event.stop_date) for p_event in planned_ids]
                    print '------ Holiday', planned_dates
                    # For each planned date, find the session that overlap with this. -> delete those sessions
                    # Also must check if the Exam period is fit for Which Student Academic year
                    if planned_ids:
    #                     print '===== HoLIDAy', planned_dates
                        for p_event in planned_ids:
                            # Planned event only apply for certain student batches
                            # Check if the current course' student batch is in the Event's 
                            # If course's year batch not in the event's batch list, -> skip this event.
                            if p_event.year_batch_ids:
                                if record.offer_course_id.academic_year_id.year_batch_id.id not in p_event.year_batch_ids.ids:
                                    continue
                                
                            study_session_ids = self.env['calendar.event'].search([('study_period_id','=', record.id),])
    #                         print '======= Sessions', study_session_ids                    
                            for session in study_session_ids:
                                           
                                # Recurring events will have the date in the name
                                if session.recurrency:
                                            session_date = get_date_from_event_id(session.id)
                                else: # Otherwise only 1 date, get the start_date
                                    session_date = session.start_date
                                    
                                if p_event.start_date <= session_date <= p_event.stop_date:
    #                                 print 'Delete ----', session.id
                                    session.unlink() 
        return super(StudyPeriod,self).write(vals)
                    
                
    
            