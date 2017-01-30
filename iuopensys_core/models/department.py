from openerp import models, fields, api
from openerp.exceptions import ValidationError

class Department(models.Model):
    
    _name = 'department'
    _description = 'Department'
    
    name = fields.Char(string='Department Name', required=True)
    dept_code = fields.Char(string='Department Code', required=True)
    dept_academic_code = fields.Char(string='Department Academic Code', required=True)
    dept_office_room =  fields.Char(string='Office Room', required=True)
    # Will be changed to Many2one after Lecturer is implemented
    head_dept_id = fields.Many2one('lecturer', string='Department Dean',
                                   help='Head of Department')
    vice_dept_id = fields.Many2one('lecturer', string='Department Vice Dean',
                                   help='Vice Dean of Department')
#     head_dept_title = fields.Char(string='Title', compute='_get_lecturer_title',
#                                   store=True)
#     
    @api.constrains('vice_dept_id', 'head_dept_id')
    def _check_dept_management(self):
        for record in self:
            if record.head_dept_id.id and record.vice_dept_id.id:
                if record.head_dept_id.id == record.vice_dept_id.id:
                    raise ValidationError('Head and Vice Dean of Department must be different')
            
        
        