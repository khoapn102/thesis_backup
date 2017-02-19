from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError

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
    semester_id = fields.Many2one('semester', string='Semester',)                                  
    offer_course_ids = fields.Many2many('offer.course', string='Offer Courses')
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
            if record.offer_course_ids:
                sum = 0
                for course in record.offer_course_ids:
                    # Check if course added is unvail
                    if course.avail_students == 0:
                        raise ValidationError('Some courses are not available (colored RED). Please choose different course.')
                    # Check for max credits
                    sum += course.course_id.number_credits
                    if sum > record.crs_reg_id.max_credits:
                        temp = record.crs_reg_id.max_credits
                        raise ValidationError('Cannot register for more than ' + str(temp))
                    
    @api.model
    def create(self, vals):
        vals['is_created'] = True
        curr_reg = super(StudentRegistration,self).create(vals)        
        return curr_reg
    
    @api.multi
    def write(self, vals):
        """
        1. Check Regsitration time
        2. 
        """
        for record in self:
            now = datetime.now()
            start = datetime.strptime(record.start_datetime, '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(record.end_datetime,'%Y-%m-%d %H:%M:%S')
            if not start <= now <= end:
                raise ValidationError('Out of Registration Period. Please try again later !')
            else:
                if 'offer_course_ids' in vals:
                    sum_cred = 0
                    for course in record.offer_course_ids:
                        sum_cred += course.number_credits
                        
                    
        return super(StudentRegistration,self).write(vals)
        
