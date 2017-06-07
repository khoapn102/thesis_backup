from openerp import models, fields, api

class Lecturer(models.Model):
    
    _name = 'lecturer'
    _inherits = {'res.users': 'user_id'}
    _description = 'IU Lecturers'
    _order = 'department_id, id'
    
    # Fields
    user_id = fields.Many2one('res.users', string='User',
                              required=True, ondelete="cascade")
    title = fields.Selection(selection=[('dr', 'Dr.'), ('mr', 'Mr.'),
                                        ('mrs', 'Mrs.'), ('ms', 'Miss')],
                             string='Title')
    
    gender = fields.Selection(selection=[('m', 'Male'), ('f', 'Female')],
                              string='Gender')
    department_id = fields.Many2one('department', string='Department')
    country_id = fields.Many2one('res.country', string='Country',
                                 default=lambda self: self.env['res.country'].
                                 search([('id', '=', 243)]))
    head_dept_id = fields.Many2one('lecturer', string='Department Dean',
                                   related='department_id.head_dept_id')
    vice_dept_id = fields.Many2one('lecturer', string='Deaprtment Vice Dean',
                                   related='department_id.vice_dept_id')
    position = fields.Selection(selection=[('dean', 'Dean'),
                                           ('vice', 'Vice Dean'),
                                           ('lecturer', 'Lecturer')],
                                string='Position', default='lecturer')
    office_room = fields.Char(string='Office Room', size=10)
    
    groups_id = fields.Many2many('res.groups', string='Security Level',
                                 related='user_id.groups_id',
                                 domain=[('name', '=', 'IU Lecturer/Staff')])
    
    # Automatically set Security when create Lecturer
    @api.onchange('title')
    def onchange_title(self):
        group_id = self.env['res.groups'].search([('name','=', 'IU Lecturer/Staff')])
        self.groups_id = group_id
    
    @api.multi
    def unlink(self):
        """
        Delete User when this record is deleted
        """
        for record in self:
            self.user_id.unlink()
            return super(Lecturer, self).unlink()
    