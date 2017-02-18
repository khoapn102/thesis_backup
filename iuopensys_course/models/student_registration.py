from openerp import models, fields, api
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
    
    @api.constrains('offer_course_ids')
    def _validate_registered_course(self):
        for record in self:
            if record.offer_course_ids:
                sum = 0
                for course in record.offer_course_ids:
                    sum += course.course_id.number_credits
                    if sum > record.crs_reg_id.max_credits:
                        temp = record.crs_reg_id.max_credits
                        raise ValidationError('Cannot register for more than ' + str(temp))
    @api.model
    def create(self, vals):
        vals['is_created'] = True
        curr_reg = super(StudentRegistration,self).create(vals)        
        return curr_reg
    
#     @api.multi
#     def write(self, vals):
#         """
#         1. Check Regsitration time
#         2. 
#         """
        
