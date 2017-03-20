from openerp import models, fields, api

class IuDocument(models.Model):
    
    _name = 'iu.document'
    _description = 'Documents Required/Produced by IU'
    
    name = fields.Char('Document\'s Name')
    doc_created_date = fields.Date('Creation Date')
    doc_signed_date = fields.Date('Signed Date')
    is_signed = fields.Boolean('Signed')
    signee_name = fields.Char('Signee')