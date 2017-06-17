from openerp import models, fields, api

class StudentAcademicProgram(models.Model):
    
    _name = 'student.academic.program'
    _description = 'Student Program at IU'
    
    name = fields.Char('Program Name')
    program_type = fields.Selection(selection=[('iu', 'IU Program'),
                                               ('foreign', 'Twining Program')],
                                    string='Program Type')
    program_code = fields.Char('Program Code')
    
    # IU Program
    std_grad_year = fields.Integer('Standard Graduation Years')
    max_grad_year = fields.Integer('Maximum Graduation Years')
    is_req_perms = fields.Boolean('Permission Required', default=True)
    min_year_req_perms = fields.Integer('Min. Years for Permission')
    
    # Twining Program
    partner_uni_id = fields.Many2one('partner.university', 'Partner University')
    grad_uni_id = fields.Many2one('partner.university', 'Certificate provided by')
    study_uni_first_id = fields.Many2one('partner.university', 'Study at (1st Phase)',
                                         default=lambda self: self.env['partner.university'].search([('school_code','=','IU')])[0])
    study_uni_second_id = fields.Many2one('partner.university', 'Stduy at (2nd Phase)')
    study_year_first = fields.Integer('Duration (1st Phase)')
    study_year_second = fields.Integer('Duration (2nd Phase)')
    
    # Required Document
    iu_doc_ids = fields.Many2many('iu.document', string='Required Documents')
    
    # Required Curriculum (SHCD, etc.)
    req_curriculum_ids = fields.Many2many('iu.curriculum', string='Required Curriculum')
    
    # Tuition Est. Information
    tuition_at_iu = fields.Float(string='IU Tuition (per yr.)')
    tuition_at_partner = fields.Float(string='Partner Tuition (per yr.)')    
    
    @api.onchange('study_year_first', 'study_year_second')
    def onchange_study_length(self):
        for record in self:
            if record.study_year_first or record.study_year_second:
                record.name = 'Twining Prog' + '-' + record.partner_uni_id.school_code
                record.name += ' (' + str(record.study_year_first) + '+' + str(record.study_year_second) + ')'
                 
    @api.onchange('partner_uni_id')
    def onchange_partner_uni(self):
        for record in self:
            if record.partner_uni_id:
                record.grad_uni_id = record.partner_uni_id.id
                record.name += '-' + record.partner_uni_id.school_code
                record.study_uni_second_id = record.partner_uni_id.id
    
    @api.onchange('program_type')
    def onchange_program_type(self):
        for record in self:
            if record.program_type:
                if record.program_type == 'iu':
                    record.name = 'IU Program'
                elif record.program_type == 'foreign':
                    record.name = 'Twining Prog'
        
    