from openerp import models, fields, api

class CourseRegistration(models.Model):
    
    _name = 'course.registration'
    _description = 'Course Registration and Configuration'
    
    name = fields.Char(string='Name', compute='_generate_name')
    semester_id = fields.Many2one('semester', string='Semester')
    year_batch_id = fields.Many2one('year.batch', string='Student Batch')
    
    @api.multi
    def _generate_name(self):
        for record in self:
            record.name = 'Registration for Batch ' + (record.year_batch_id.year_code or "")
            
    
              
    
    