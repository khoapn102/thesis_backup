from openerp import models, fields, api

class Course(models.Model):
    
    _name = 'course'
    _description = 'IU Course'
    
    name = fields.Char(string='Course Name', size=128)
    department_id = fields.Many2one('department', string='Department', required=True)
    number_credits = fields.Integer(string='Number of Credits', required=True)
    prereq_course_id = fields.Many2one('course', string='Prerequisite Course')
    course_type = fields.Selection(selection=[('compulsory', 'Compulsory'),
                                              ('elective', 'Elective')],
                                   string='Course Type',
                                   help='Type of a Course: Compulsory or Elective')
    offer_course_ids = fields.One2many('offer.course', 'course_id', 'Offering Courses')
    
    #Period_id (for scheduling)
    
    