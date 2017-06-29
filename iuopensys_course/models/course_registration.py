from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class CourseRegistration(models.Model):
    
    _name = 'course.registration'
    _description = 'Course Registration Configuration'
    
    # Default functions Here
    def _default_reg_semester_id(self):
        res = self.env['semester'].search([],limit=1,order='id desc')
        return res and res[0] or False
    
    # Fields
    name = fields.Char(string='Name', default='Registration for Batch ')
    # Courses reference this one
    reg_semester_id = fields.Many2one('semester', string='Semester',
                                default=_default_reg_semester_id)
    year_batch_id = fields.Many2one('year.batch', string='Student Batch',
                                    required=True)
    start_datetime = fields.Datetime(string='Start at',
                                     default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    end_datetime = fields.Datetime(string='End at',
                                   default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    drop_deadline_datetime = fields.Datetime(string='Drop Deadline', default=lambda self: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                             help='Deadline for latest dropping course without getting charged 30% fee')
    max_credits = fields.Integer(string='Maximum Credits', default=24)
    min_credits = fields.Integer(string='Minimum Credits', default=12)
        
    @api.onchange('year_batch_id')
    def _onchange_year_batch_id(self):
        self.name += (self.year_batch_id.year_code or "")
        
    @api.constrains('start_datetime','end_datetime')
    def _check_valid_time(self):
        "End must be at least 1 hr away from start"
        format = '%Y-%m-%d %H:%M:%S'
        for record in self:
            start = datetime.strptime(record.start_datetime,format)
            end = datetime.strptime(record.end_datetime,format)
            diff = int((end-start).seconds)
            if diff == 0:
                raise ValidationError('End time must be different from Start time !')
        
    @api.model
    def create(self, vals):
        curr_reg = super(CourseRegistration,self).create(vals)
        # Search for all students in this batch and assign Registration Form
        student_ids = self.env['student'].search([('year_batch_id','=',curr_reg.year_batch_id.id),
                                                  ('graduation_status','in',['ie','ontrack','complete'])])
        for student in student_ids:
            # Student Registration
            new_vals = {'crs_reg_id':curr_reg.id,
                        'student_id':student.id,
                        'semester_id':curr_reg.reg_semester_id.id,
                        'is_created':True}
            self.env['student.registration'].create(new_vals)
            
            # Student Semester -> for tracking each Semester
            new_vals = {'student_id': student.id,
                        'semester_id': curr_reg.reg_semester_id.id,}
            self.env['student.semester'].create(new_vals)
            
        return curr_reg
    
        
              
    
    