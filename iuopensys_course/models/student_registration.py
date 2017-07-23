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
    drop_deadline = fields.Datetime(related='crs_reg_id.drop_deadline_datetime')
    
    # Student Related Info
    student_id = fields.Many2one('student', string='Student')
    department_id = fields.Many2one(related='student_id.department_id')
    user_id = fields.Many2one(related='student_id.user_id')
    accumulated_creds = fields.Integer(related='student_id.accumulated_credits')  # store=True # Add when DEMO
    major_id = fields.Many2one('major', related='student_id.major_id')
    course_ids = fields.Many2many('course', related='major_id.course_ids')
    
    exam_status = fields.Boolean(string='Exam Status', related='student_id.exam_status')
    semester_id = fields.Many2one('semester', string='Semester')
    dept_academic_sem = fields.Char('Dept-Semester', compute='get_dept_academic_semester',
                                    store=True,
                                    help='Search by Department-Year-Semester. e.g: IT1320131')
    
    offer_course_ids = fields.Many2many('offer.course', string='Offer Courses',)
    drop_course_ids = fields.Many2many('offer.course', 'offer_course_student_registration_drop_rel', 
                                    'student_registration_id',
                                    'offer_course_id',
                                    string='Dropped Courses',
                                    help='Student will be charged 30% tuition.')
    temporary_drop_crs_ids = fields.Many2many('offer.course', 'offer_course_student_registration_temporary_rel',
                                              'student_registration_id',
                                              'offer_course_id',
                                              string='Temporary Drops',
                                              help='Re-register for courses that are allowed by advisor. No-charge')
    
    # To set other field to be readonly
    is_created = fields.Boolean(string='Created', default=False)
#     reg_state = fields.Selection(selection=[('draft', 'Draft'),
#                                             ('confirm', 'Confirmed'),
#                                             ('approve', 'Approved'),
#                                             ('deny', 'Denied'),                                          
#                                             ], string='State',
#                                  default='draft')
    reg_state = fields.Selection(selection=[('draft', 'Draft'),
                                            ('confirm', 'Confirmed'),
                                            ], string='State',
                                 default='draft')
    
    ext_note = fields.Text('Note')
    advisor_note = fields.Text('Advisor\'s Note')
    
    # Student Tuition per Semester with Financial Aid calculation
    student_balance = fields.Float('Current balance', related='student_id.student_balance')
    # Student Debt here to check if student allow to register for upcoming semester. Must pay last one
    student_debt = fields.Float('Student Debt', related='student_id.student_debt')
    total_creds = fields.Integer('Total credits registered', compute='get_tuition_info', default=0)
    stat_button_total_creds = fields.Integer('Credits', compute='get_tuition_info')
    stat_button_amount_tuition = fields.Char('Tuition', compute='get_tuition_info',)
    total_actual_creds = fields.Integer('Total actual credits', compute='get_tuition_info', default=0)
    
    amount_tuition = fields.Float('Tuition amount', compute='get_tuition_info')
    
#     amount_tuition_discount = fields.Float('Amount discount', compute='get_tuition_info')
    
    amount_financial_aid = fields.Float('Financial Aid amount')
    
#     amount_financial_aid_with_discount = fields.Float('Total discount amount', compute='get_tuition_info')
    
    amount_paid = fields.Float('Amount paid')

    amount_must_pay = fields.Float('Amount must pay', compute='get_tuition_info')
    
    amount_leftover = fields.Float('Amount owned', compute='_get_amt_leftover')
    
    is_full_paid = fields.Boolean('Paid in full')
        
    in_period = fields.Boolean('In Reg Time', compute='_check_in_period')
    
    toggle_view_temp = fields.Boolean('Toggle', compute='toggle_view')
    
    @api.depends('temporary_drop_crs_ids')
    def toggle_view(self):
        for record in self:
            if len(record.temporary_drop_crs_ids) > 0:
                record.toggle_view_temp = True
            else:
                record.toggle_view_temp = False

    @api.depends('student_id','semester_id')
    def get_dept_academic_semester(self):
        for record in self:
            record.dept_academic_sem = record.student_id.department_id.dept_academic_code or '' +\
                                            str(int(record.student_id.year_batch_id.year or 0)%100) or '' +\
                                            record.semester_id.semester_code or ''
    
    @api.multi
    def deduct_from_student_balance(self):
        for record in self:
            if not record.is_full_paid:
                if record.amount_tuition >0 and record.student_balance > 0:
                    
                    new_balance = 0 if record.student_balance < record.amount_tuition else record.student_balance - record.amount_tuition
                     
                    if record.student_balance < record.amount_tuition and\
                        record.student_balance < record.amount_must_pay:
                        amount_paid = record.student_balance
                    else:
                        amount_paid = record.amount_must_pay
                    
                    vals = {'amount_paid': amount_paid,
                            'student_balance': new_balance}
                    if amount_paid == record.amount_tuition:
                        vals['is_full_paid'] = True
                    
                    record.write(vals)
            else:
                raise ValidationError('Cannot deduct from student balance. Please check again!') 
                    
    # Update Registration note for Advisor
    @api.onchange('offer_course_ids')
    def onchange_offer_course_ids(self):
        self.ext_note = ''
        if self.offer_course_ids:
#             print '=======', self.total_creds
            # Check Course prerequesite
#             print '====', self.ext_note
#             self.ext_note = 'Courses needs Prereq. completion:'
#             
#             check = False
#             
#             for course in self.offer_course_ids:
#                 if course.prereq_course_id: # Found Course prereq
#                     prereq_offer_ids = course.prereq_course_id.offer_course_ids
# #                     print '====== PRE', prereq_offer_ids
#                     # Search Student_course to check if satisfied requirements
#                     student_course_ids = self.env['student.course'].search([('student_id','=', self.student_id.id),
#                                                                             ('offer_course_id','in',prereq_offer_ids.ids),
#                                                                             ('is_complete','=',True)])
# #                     print '======= STD', student_course_ids
#                     if not student_course_ids: # Cant find prereq completed
#                         check = True
#                         self.ext_note += '\n\t- ' + course.name + ' (' + course.prereq_course_id.name +')'
#                     
#             if not check:
#                 self.ext_note += ' N/A'
            
            if self.total_creds < self.crs_reg_id.min_credits:
                self.ext_note += 'Register under minimum credits required.'
        else:
            self.ext_note = ''
    
    @api.one
    def paid_in_full(self):
        self.write({'is_full_paid': not self.is_full_paid})
        if self.is_full_paid:
            self.write({'amount_paid': self.amount_must_pay})
            if not self.exam_status:
                self.write({'exam_status': not self.exam_status})
        else:
            self.write({'amount_paid': 0})
            
    # Checkin Period - Register Time
    def _check_in_period(self):
        now = datetime.now()
        start = datetime.strptime(self.start_datetime, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(self.end_datetime,'%Y-%m-%d %H:%M:%S')
        if (start <= now <= end):
            self.in_period = True
        else:
            self.in_period = False

    # Calculate Tuition base on Courses Registered
    @api.depends('offer_course_ids')
    def get_tuition_info(self):
        for record in self:
            cred = 0
            tuition = 0
            financial_aid_value = 0
#             tuition_disc_val = 0
            # Get Tuition for all Registered Courses
            if record.offer_course_ids:
                for course in record.offer_course_ids:
                    cred += course.course_id.number_credits
                    tuition += course.crs_tuition
            if record.drop_course_ids:
                for course in record.drop_course_ids:
                    tuition += 0.3*(course.crs_tuition)
                    
            # Check if student has Financial Aid
#             if record.student_id.financial_aid_id:
#                 financial_aid = record.student_id.financial_aid_id
#                 start = datetime.strptime(financial_aid.start_date,"%Y-%m-%d")
#                 end = datetime.strptime(financial_aid.end_date,"%Y-%m-%d")
#                 
#                 # Check if the financial aid is valid (is_active and in valid date range)
#                 if financial_aid.is_active and (start <= datetime.now() <= end):
#                     if financial_aid.finance_type == 'percent':
#                         financial_aid_value = tuition * financial_aid.finance_value/100
#                     elif financial_aid.finance_type == 'amount':
#                         financial_aid_value = financial_aid.finance_value
            
            # Check student balance has money -> deduct from there:
#             if record.student_id.student_balance > 0:
#                 if record.student_id.tuition_discount:
#                     tuition_disc_val = tuition * 0.1
            
#             total_discount_amt = financial_aid_value + tuition_disc_val
                                  
            record.total_creds = cred
            record.total_actual_creds = cred
            record.amount_tuition = tuition
#             record.amount_tuition_discount = tuition_disc_val
#             record.amount_financial_aid = financial_aid_value
#             record.amount_financial_aid_with_discount = total_discount_amt
            
#             amount_must_pay = tuition - total_discount_amt
             
#             record.amount_must_pay = 0 if total_discount_amt >= tuition else amount_must_pay
            record.amount_must_pay = tuition
            # Incase student's has financial aid cover 100% tuition no matter what
#             if financial_aid_value == tuition:
#                 record.amount_must_pay = tuition - financial_aid_value
#             elif total_discount_amt >= tuition:
#                 record.amount_must_pay = 
#             
#             if record.amount_must_pay == 0:
#                 record.is_full_paid = True
            
            # Student debt is update
#             student_debt = record.student_id.student_debt
#             print '==== Before: ', student_debt
#             student_debt += record.amount_must_pay
#             print '==== After:', student_debt
            
#             student_id = self.env['student'].search([('id','=',record.student_id.id)])
#             if student_id:
#                 student_id.write({'student_debt':student_debt})
                
#             record.student_id.student_debt = student_debt
#             print '========', record.student_id.student_debt
            
            record.stat_button_total_creds = cred
            record.stat_button_amount_tuition = str(tuition) + ' USD'
            
#             print '++++ course_ids', student_id.major_id.course_ids.ids
            
    @api.onchange('is_full_paid')
    def _onchange_full_paid(self):
        if self.is_full_paid:
            self.amount_paid = self.amount_must_pay
        else:
            self.amount_paid = 0
    
    @api.depends('amount_paid')
    def _get_amt_leftover(self):
        for record in self:
            record.amount_leftover = record.amount_must_pay - record.amount_paid
            # Update amount must pay now
            record.amount_must_pay = record.amount_leftover
#             student_id = self.env['student'].search([('id','=',record.student_id.id)])
#             if student_id:
#                 student_id.write({'student_debt':record.amount_leftover})
    
#     @api.constrains('amount_paid','amount_must_pay')                    
                    
    @api.constrains('offer_course_ids')
    def _validate_registered_course(self):
        for record in self:
            
            # Check for tuition debt
            student_reg_ids = self.env['student.registration'].search([('student_id','=',record.student_id.id),
                                                                       ('is_full_paid','=',False)])
#             print 'NOOOOWWWW', student_reg_ids, ' ', record.id
            tuition_debt = student_reg_ids.ids
            if tuition_debt:
                if record.id in tuition_debt:
                    tuition_debt.remove(record.id) # Remove itself record
                
            if tuition_debt:    
                raise ValidationError('Student must pay tuition debt before registering this semster.')
            
            sum = 0
            check_overload = 0
            check_overlap = 0
            
            check_prereq = 0
            check_under_minimum = 0
            check_extra_constraints = 0
#             check_avail = 0
                        
            if record.offer_course_ids:
                reg_sched = {}
                
                pre_req_note = ''                
                
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
                    
#                   # Check Prereq if being asked            
                    if course.prereq_course_id: # Found Course prereq
                        prereq_offer_ids = course.prereq_course_id.offer_course_ids
                        # Search Student_course to check if satisfied requirements
                        student_course_ids = self.env['student.course'].search([('student_id','=', self.student_id.id),
                                                                                ('offer_course_id','in',prereq_offer_ids.ids),
                                                                                ('is_complete','=',True)])
                        if not student_course_ids:
                            check_prereq = 1
                            pre_req_note += course.name + ' (' + course.prereq_course_id.name +')' +' - Incomplete Prerequesites.\n'
                    
                    # Check if extra constraints satisfied (> accum. creds)
                    if course.req_extra_constraints:
                        if record.accumulated_creds < course.accum_cred_gt_value:
                            check_extra_constraints = 1
                            pre_req_note += course.name + ' - Must have more than ' + str(course.accum_cred_gt_value) + ' credits to register.'
                                                            
                    # Check if course added is unvail
#                     if course.avail_students == 0:
#                         check_avail = 1

                    # Check for max credits
                    sum += course.course_id.number_credits
                
                for key in reg_sched:
                    temp_lst = reg_sched[key]
                    overlapping = [[x,y] for x in temp_lst for y in temp_lst if x is not y and x[1]>=y[0] and x[0]<=y[0]]
#                     print '=======', overlapping
                    if len(overlapping) > 0:
                        check_overlap = 1
                        break
                if sum > record.crs_reg_id.max_credits:
                    check_overload = 1
                if check_overload == 1:
                    raise ValidationError('Cannot register for more than ' + str(record.crs_reg_id.max_credits) + ' credits.')
                if check_overlap == 1:
                    raise ValidationError('Overlap schedule. Please check again.')
                
                student_ids = self.env['student'].search([])
                student_user_ids = [x.user_id.id for x in student_ids]
                
                if (check_prereq == 1) and (self.env.user.id in student_user_ids):
#                     pre_req_note += '\n' + 'Prerequesites are not completed.'
                    raise ValidationError(pre_req_note)
                if (check_extra_constraints == 1) and (self.env.user.id in student_user_ids):
                    raise ValidationError(pre_req_note)
                
                # Check Min reg
                if (record.total_creds < record.crs_reg_id.min_credits) and (self.env.user.id in student_user_ids):
                    raise ValidationError('Register less than minimum requirements.')
                
#                 if check_avail == 1:
#                         raise ValidationError('Some courses are not available (in Red).')

                             
                    
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
            drop_deadline = datetime.strptime(record.drop_deadline,'%Y-%m-%d %H:%M:%S')
            
            # Must be student and Out of Registration period -> Error
            if (not start <= now <= end) and (self.env.user.id in student_user_ids):
                raise ValidationError('Out of Registration Period. Please try again later !')
            # Not a student, or in Reg period, or other ..
            else:
                if 'reg_state' in vals:
#                     print vals
                    if vals['reg_state'] == 'deny':
                        print '===== Deny'
                        if record.offer_course_ids:
                            # Student already registered for course -> set to temporary_drop
                            record.temporary_drop_crs_ids = record.offer_course_ids.ids
#                             print '========', record.temporary_drop_crs_ids
                            
                            crs_ids = record.offer_course_ids.ids
                            lab_only_ids = self.env['offer.course'].search([('id', 'in', crs_ids), ('is_lab','=',True)])
                            if lab_only_ids:
                                for course in lab_only_ids:
                                    crs_ids.append(course.theory_course_id.id)
                            new_offer_course_ids = self.env['offer.course'].search([('id', 'in', crs_ids)])
                            
                            print '====== COURSE', new_offer_course_ids
                            
                            for course in new_offer_course_ids:
#                                 new_std_crs_id = self.env['student.course'].search([('student_id','=',record.student_id.id),
#                                                                                     ('offer_course_id','=', course.id)])
#                                 print '======= NOW', new_std_crs_id
# #                                 new_std_crs_id.unlink()
#                                 print 'HERE 2'
                                if course.id in record.offer_course_ids.ids:
                                    record.offer_course_ids = [(3, course.id)]
                            record.drop_course_ids = [(6,0,[])]
                    else:
                        continue
                
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
                    
#                     print '+++++++ old: ', old_ids, ' ===== curr: ' , ids
                    onchange_crs_ids = [x for x in (old_ids+ids) if\
                                         (x not in old_ids) or (x not in ids)] # After onchange
#                     print '========== onchange: ', onchange_crs_ids # Include lab only or single course
                    
                    onchange_crs_ids_copy = onchange_crs_ids[:] # Only includes what course in the form (not theory, etc.)
                    
                    lab_only_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids), ('is_lab','=',True)])
                    if lab_only_ids:
                        for course in lab_only_ids:
                            onchange_crs_ids.append(course.theory_course_id.id)
                    offer_course_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids)])
#                     print '------ updated-onchange: ', offer_course_ids # Include lab + thoery for add
                    
                    sum_cred = 0
                    
                    drop_crs = []
                    
                    remove_temp_crs = []
                    
                    for course in offer_course_ids:
                        # Do not handle course that has no avaialble slots
#                         print '+++++ Here', course.avail_students
                        if course.avail_students == 0:
                            # Student try to add unavail course, remove from VALS
                            if course.id in vals['offer_course_ids'][0][2]:
                                vals['offer_course_ids'][0][2].remove(course.id)
                                continue
                        sum_cred += course.number_credits
                        std_crs_id = self.env['student.course'].search([('student_id','=',record.student_id.id),
                                                                 ('offer_course_id','=', course.id)])
#                         print '------- New HERE', std_crs_id
                        
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
                                
                            if course.id in record.temporary_drop_crs_ids.ids:
                                vals['temporary_drop_crs_ids'] = [(3, course.id)]

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

                            if course.id in onchange_crs_ids_copy:
                                drop_crs.append(course.id)
#                             print '======== DROP', drop_crs
                            
                            std_crs_id.unlink()
                            
                        # Then add to Dropped courses if out side reg period, Only Faculty/admin allow to do
                        # Drop courses got charged if drop after the DEADLINE
                        if (not start <= now <= end) and (now > drop_deadline):
                            # Only add back the lab course to calculate money
                            vals['drop_course_ids'] = [(6, 0, drop_crs)]                           

                    vals['reg_state'] = 'confirm'
                    
        return super(StudentRegistration,self).write(vals)
        

