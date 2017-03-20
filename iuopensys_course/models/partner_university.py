from openerp import models, fields, api

class PartnerUniversity(models.Model):
    
    _name = 'partner.university'
    _description = 'Partner Universities for Twinning Program'
    
    name = fields.Char('University Name')
    uni_address = fields.Char('University Address')
    country_id = fields.Many2one('res.country', 'Country')
    