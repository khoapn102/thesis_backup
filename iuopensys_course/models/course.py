from openerp import models, fields, api

class Course(models.Model):
    
    _name = 'course'
    _description = 'IU Course'
    
    name = fields.Char(string='Course Name', size=128)
    department_id = fields.Many2one('department', string='Department', required=True)
    number_credits = fields.Integer(string='Credits', required=True)
    number_credits_actual = fields.Integer(string='Credits for Tuition', required=True)
                                           
#     prereq_course_id = fields.Many2one('course', string='Prerequisite Course',
#                                        domain="[('department_id','=',department_id)]")
    prereq_course_id = fields.Many2one('course', string='Prerequisite Course')
       
    course_type = fields.Selection(selection=[('compulsory', 'Compulsory'),
                                              ('elective', 'Elective')],
                                   string='Course Type',
                                   help='Type of a Course: Compulsory or Elective')
    crs_lang = fields.Selection(selection=[('eng', 'English'),
                                           ('vn', 'Vietnamese')],
                                default='eng',
                                string='Teaching Language')
    
#     tuition_id = fields.Many2one('course.tuition', string='Credit Cost')
    
    offer_course_ids = fields.One2many('offer.course', 'course_id', 'Offering Courses')
    cred_count_type = fields.Selection(selection=[('count', 'Normal'),
                                                  ('nocount','Only Pass/No pass')],
                                       default='count', string='Credit Count Type')
    # Extra Curricular
    is_extra_curricular = fields.Boolean(string='Extra Curricular')
          
    @api.onchange('number_credits')
    def _onchange_number_credits(self):
        self.number_credits_actual = self.number_credits