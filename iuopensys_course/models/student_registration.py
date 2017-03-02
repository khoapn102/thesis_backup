from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError, Warning

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
    
    offer_course_ids = fields.Many2many('offer.course',
                                        string='Offer Courses',)
    
    # To set other field to be readonly
    is_created = fields.Boolean(string='Created', default=False)
    reg_state = fields.Selection(selection=[('draft', 'Draft'),
                                            ('confirm', 'Confirmed'),
                                            ('approve', 'Approved'),
                                            ('reopen','Reopen'),
                                            ('done', 'Done')], string='State',
                                 default='draft')
    
    ext_note = fields.Text('Note')
    
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
            now = datetime.now()
            start = datetime.strptime(record.start_datetime, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(record.end_datetime,'%Y-%m-%d %H:%M:%S')
            if not start <= now <= end:
                raise ValidationError('Out of Registration Period. Please try again later !')
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
                    print '+++++++', old_ids, ' =====' , ids
                    onchange_crs_ids = [x for x in (old_ids+ids) if\
                                         (x not in old_ids) or (x not in ids)] # After onchange
                    print '==========', onchange_crs_ids
                    
                    lab_only_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids), ('is_lab','=',True)])
                    if lab_only_ids:
                        for course in lab_only_ids:
                            onchange_crs_ids.append(course.theory_course_id.id)
                    offer_course_ids = self.env['offer.course'].search([('id', 'in', onchange_crs_ids)])
                    print '-0-0-----', offer_course_ids
                    
                    sum_cred = 0
                    for course in offer_course_ids:
                        if course.avail_students == 0:
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
                            if course.study_session_ids:
                                # Add student to calendar
#                                 event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id)], order='id asc', limit=1)
#                                 print '++++++', event_ids
#                                 if event_ids:
#                                     event_vals = {}
#                                     for event in event_ids:
#                                         event['partner_ids'] = [(4, record.student_id.user_id.partner_id.id)]
                                for session in course.study_session_ids:
                                    event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id),
                                                                                   ('study_period_id', '=', session.id)],
                                                                                  order='id asc', limit=1)
                                    print '++++++++++', event_ids
                                    if event_ids:
                                        event_vals = {}
                                        for event in event_ids:
                                            event['partner_ids'] = [(4, record.student_id.user_id.partner_id.id)]
                        else:
                            # Delete a reg. course (use student_course model)
                            if course.study_session_ids:
                                for session in course.study_session_ids:
                                    event_ids = self.env['calendar.event'].search([('offer_course_id','=',course.id),
                                                                                   ('study_period_id', '=', session.id)],
                                                                                  order='id asc', limit=1)
                                    print '======', event_ids
                                    if event_ids:
                                        for event in event_ids:
                                            event.partner_ids = [(3, std_crs_id.student_id.user_id.partner_id.id)]
                                            print '======Event Partner =====', event.partner_ids
                            std_crs_id.unlink()                            

                    vals['reg_state'] = 'confirm'
                    if sum_cred < record.crs_reg_id.min_credits:
                        vals['ext_note'] = 'Register under minimum credits required.'
                    
        return super(StudentRegistration,self).write(vals)
        
