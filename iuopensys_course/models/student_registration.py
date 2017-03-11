from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError, Warning
from openerp import SUPERUSER_ID

class StudentRegistration(models.Model):
    
    _name = 'student.registration'
    _description = 'Student Registration Form'
    
    name = fields.Char(string='Name', default='Registration Form', readonly=True)
    crs_reg_id = fields.Many2one('course.registration', string='Registration', ondelete="cascade")
    start_datetime = fields.Datetime(string='Start at',
                                     related='crs_reg_id.start_datetime')
    end_datetime = fields.Datetime(string='End at',
                                   related='crs_reg_id.end_datetime')
    student_id = fields.Many2one('student', string='Student')
    semester_id = fields.Many2one('semester', string='Semester')
    
    offer_course_ids = fields.Many2many('offer.course', string='Offer Courses',)
    drop_course_ids = fields.Many2many('offer.course', 'offer_course_student_registration_drop_rel', 
                                    'student_registration_id',
                                    'offer_course_id',
                                    string='Dropped Courses')
    
    # To set other field to be readonly
    is_created = fields.Boolean(string='Created', default=False)
    reg_state = fields.Selection(selection=[('draft', 'Draft'),
                                            ('progress', 'Processing'),
                                            ('confirm', 'Confirmed'),
                                            ('approve', 'Approved'),
                                            ('reopen','Reopen'),
                                            ('paid', 'Paid')], string='State',
                                 default='draft')
    
    ext_note = fields.Text('Note')
    
    # Student Tuition per Semester
    student_balance = fields.Float('Current balance', related='student_id.student_balance')
    total_creds = fields.Integer('Total credits registered', compute='get_tuition_info', default=0)
    stat_button_total_creds = fields.Integer('Credits', compute='get_tuition_info')
    stat_button_amount_tuition = fields.Char('Tuition', compute='get_tuition_info',)
    total_actual_creds = fields.Integer('Total actual credits', compute='get_tuition_info', default=0)
    amount_tuition = fields.Float('Tuition amount', compute='get_tuition_info')
    amount_paid = fields.Float('Amount paid')
    amount_leftover = fields.Float('Amount owned', compute='_get_amt_leftover')
    is_full_paid = fields.Boolean('Paid in full')    
    
    in_period = fields.Boolean('In Reg Time', compute='_check_in_period')
    
    def _check_in_period(self):
        now = datetime.now()
        start = datetime.strptime(self.start_datetime, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(self.end_datetime,'%Y-%m-%d %H:%M:%S')
        if (start <= now <= end):
            self.in_period = True
        else:
            self.in_period = False
#     @api.multi
#     def edit_form_view(self):
#         self.is_edit_mode = True
#         return {
#                 'name': "Registration Form",
#                 'type': 'ir.actions.act_window',
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'res_model': 'student.registration',
#                 'res_id': self.id,                
#                 'target': 'inline',
#                 'context': self._context,
#                 }

    @api.depends('offer_course_ids')
    def get_tuition_info(self):
        for record in self:
            cred = 0
            tuition = 0
            if record.offer_course_ids:
                for course in record.offer_course_ids:
                    cred += course.course_id.number_credits
                    tuition += course.crs_tuition
            if record.drop_course_ids:
                for course in record.drop_course_ids:
                    tuition += 0.3*(course.crs_tuition)
            record.total_creds = cred
            record.total_actual_creds = cred
            record.amount_tuition = tuition
            record.stat_button_total_creds = cred
            record.stat_button_amount_tuition = str(tuition) + ' USD'
            print '++++ UID', SUPERUSER_ID
            
    @api.onchange('is_full_paid')
    def _onchange_full_paid(self):
        if self.is_full_paid:
            self.amount_paid = self.amount_tuition
    
    @api.depends('amount_paid')
    def _get_amt_leftover(self):
        for record in self:
            record.amount_leftover = record.amount_tuition - record.amount_paid
                    
    @api.constrains('offer_course_ids')
    def _validate_registered_course(self):
        for record in self:
            sum = 0
            check_overload = 0
            check_overlap = 0           
            if record.offer_course_ids:
                reg_sched = {}
                for course in record.offer_course_ids:
                    # Check if any course has same reg time
                    if course.is_lab:
                        theory_crs = course.theory_course_id
                        if theory_crs.study_session_ids:
                            for session in theory_crs.study_session_ids:
                                if session.crs_day in reg_sched:
                                    reg_sched[session.crs_day].append((session.start_time, session.end_time))
                                else:
                                    reg_sched[session.crs_day] = [(session.start_time, session.end_time)]
                    if course.study_session_ids:                     
                        for session in course.study_session_ids:
                            if session.crs_day in reg_sched:
                                reg_sched[session.crs_day].append((session.start_time, session.end_time))
                            else:
                                reg_sched[session.crs_day] = [(session.start_time, session.end_time)]
                                                            
                    # Check if course added is unvail
#                     if course.avail_students == 0:
#                         raise ValidationError('Some courses are not available (in Red).')
                    # Check for max credits
                    sum += course.course_id.number_credits
                
                for key in reg_sched:
                    temp_lst = reg_sched[key]
                    overlapping = [[x,y] for x in temp_lst for y in temp_lst if x is not y and x[1]>=y[0] and x[0]<=y[0]]
                    if len(overlapping) > 0:
                        check_overlap = 1
                        break
                if sum > record.crs_reg_id.max_credits:
                    check_overload = 1
                if check_overload == 1:
                    raise ValidationError('Cannot register for more than ' + str(record.crs_reg_id.max_credits) + ' credits.')
                if check_overlap == 1:
                    raise ValidationError('Overlap schedule. Please check again.')
    
#     @api.onchange('offer_course_ids')
#     def _onchange_offer_course(self):
#         if self.offer_course_ids:
#             course_ids = []
#             for course in self.offer_course_ids:
#                 if course.avail_students == 0:
#                     course_ids.append((3,course.id))
# #                     print '++++++', self.offer_course_ids
# #                     print '++++++', self.offer_course_ids
# #                     raise Warning('Course is not available (in Red). Please remove selection')
#                     print '+++++', self.offer_course_ids
#                     self.offer_course_ids = [(3,course.id)]
#                     print '++++++', self.offer_course_ids
#             return {'value': {'offer_course_ids': course_ids}}                           
                    
    @api.model
    def create(self, vals):
        vals['is_created'] = True
        curr_reg = super(StudentRegistration,self).create(vals)        
        return curr_reg
    
    @api.multi
    def write(self, vals):
        """
        1. Check Regsitration time
        2. Register course for student
            1. 
        3. Add student to the calendar event
        """
        for record in self:
            
            # Faculty/Admin user allow to bypass reg time
            student_ids = self.env['student'].search([])
            student_user_ids = [x.user_id.id for x in student_ids]    
                        
            now = datetime.now()
            start = datetime.strptime(record.start_datetime, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(record.end_datetime,'%Y-%m-%d %H:%M:%S')
            # Must be student and Out of Registration period -> Error
            if (not start <= now <= end) and (self.env.user.id in student_user_ids):
                raise ValidationError('Out of Registration Period. Please try again later !')
            # Not a student, or in Reg period, or other ..
            else:
                if 'offer_course_ids' in vals:
                    # Create Registration if there is none
                    """
                    1. Check if there course is in vals (unlink/write affect)
                    2. Retrieve all the related course in vals 
                    **** All Courses in the reg is either a lab or course has no lab.
                    **** Must check for course theory schedule if it has
                    3. Compare with current record. If current ids from vals different
                    4. Adapt the change. The unlink will be deleted and the extra will be added 
                    """                    
                    ids = vals['offer_course_ids'][0][2] # Current courses reg (at onchange)
#                     # Remove course has 0 avail students
#                     remv_crs_ids = self.env['offer.course'].search([('id','in',ids),('avail_students', '>', 0)])
#                     if remv_crs_ids:
#                         for course in remv_crs_ids:
#                             ids.remove(course.id)
                            
                    old_ids = [a.id for a in record.offer_course_ids] # Old courses reg (before onchange)
                    drop_ids = [a.id for a in record.drop_course_ids] # Drop courses
                    
                    print '+++++++ old: ', old_ids, ' ===== curr: ' , ids
                    onchange_crs_ids = [x for x in (old_ids+ids) if\
                                         (x not in old_ids) or (x not in ids)] # After onchange
                    print '========== onchange: ', onchange_crs_ids
                    
                    lab_only_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids), ('is_lab','=',True)])
                    if lab_only_ids:
                        for course in lab_only_ids:
                            onchange_crs_ids.append(course.theory_course_id.id)
                    offer_course_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids)])
                    print '------ updated-onchange: ', offer_course_ids
                    
                    sum_cred = 0
                    for course in offer_course_ids:
                        # Do not handle course that has no avaialble slots
                        print '+++++ H', course.avail_students
                        if course.avail_students == 0:
                            # Student try to add unavail course, remove from VALS
                            if course.id in vals['offer_course_ids'][0][2]:
                                vals['offer_course_ids'][0][2].remove(course.id)
                                continue
                        sum_cred += course.number_credits
                        std_crs_id = self.env['student.course'].search([('student_id','=',record.student_id.id),
                                                                 ('offer_course_id','=', course.id)])
                        print '-------', std_crs_id
                        if not std_crs_id:
                            # New course for reg
                            new_vals = {
                                        'student_id': record.student_id.id,
                                        'offer_course_id': course.id,
                                        }
                            self.env['student.course'].create(new_vals) # Reg for student
                            
                            # Re added dropped course. In case
                            if course.id in drop_ids:
                                vals['drop_course_ids'] = [(3, course.id)]

#                             if course.study_session_ids:
#                                 # Add student to calendar
# #                                 event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id)], order='id asc', limit=1)
# #                                 print '++++++', event_ids
# #                                 if event_ids:
# #                                     event_vals = {}
# #                                     for event in event_ids:
# #                                         event['partner_ids'] = [(4, record.student_id.user_id.partner_id.id)]
#                                 for session in course.study_session_ids:
#                                     event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id),
#                                                                                    ('study_period_id', '=', session.id)],
#                                                                                   order='id asc', limit=1)
#                                     print '++++++++++', event_ids
#                                     if event_ids:
#                                         event_vals = {}
#                                         for event in event_ids:
#                                             event['partner_ids'] = [(4, record.student_id.user_id.partner_id.id)]
                        else:
                            # Delete a reg. course (use student_course model)
#                             if course.study_session_ids:
#                                 for session in course.study_session_ids:
#                                     event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id),
#                                                                                    ('study_period_id', '=', session.id)],
#                                                                                   order='id asc', limit=1)
#                                     print '======', event_ids
#                                     if event_ids:
#                                         for event in event_ids:
#                                             event.partner_ids = [(3, std_crs_id.student_id.user_id.partner_id.id)]
#                                             print '======Event Partner =====', event.partner_ids

                            std_crs_id.unlink()
                            
                            # Then add to Dropped courses if out side reg period, Only Faculty/admin allow to do
                            if (not start <= now <= end):
                                vals['drop_course_ids'] = [(4, course.id)]                           

                    vals['reg_state'] = 'confirm'
                    if sum_cred < record.crs_reg_id.min_credits:
                        vals['ext_note'] = 'Register under minimum credits required.'
                    
        return super(StudentRegistration,self).write(vals)
        
