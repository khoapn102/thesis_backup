from openerp import models, fields, api

class StudentAcademicProgram(models.Model):
    
    _name = 'student.academic.program'
    _description = 'Student Program at IU'
    
    name = fields.Char('Program Name')
    diploma_type = fields.Selection(selection=[('iu', 'International University'),
                                               ('foreign', 'Foreign University')])
    
    # IU Program
    std_grad_period = fields.Integer('Standard Graduation Years')
    max_grad_period = fields.Integer('Maximum Graduation Years')
    is_req_extra_doc = fields.Boolean('Permission Required')
    min_time_require = fields.Integer('Min. Years requires Permission')
    
    # Twining Program
    partner_uni_id = fields.Many2one('partner.university', 'Partner University')
    grad_uni_id = fields.Many2one('partner.university', 'Certificate provided from')
    study_uni_id = fields.Many2one('partner.university', 'Study at')
    study_length_iu = fields.Integer('Study at IU')
    study_length_partner = fields.Integer('Study at Partner University')
    
    @api.onchange('study_length_iu', 'study_length_partner')
    def onchange_study_length(self):
        for record in self:
            if record.study_length_iu or record.study_length_partner:
                record.name = (record.name + ' - (' + record.study_length_iu + '+' + record.study_length_partner)
                 
                
    
    