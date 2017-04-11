from openerp import models, fields, api

class IuDocument(models.Model):
    
    _name = 'iu.document'
    _description = 'Documents Required/Produced by IU'
    
    # Fields    
    name = fields.Char('Document\'s Name')
    doc_type = fields.Selection(selection=[('student', 'Student'),
                                           ('university', 'University')],
                                string='Provided By')
    doc_signed_date = fields.Date('Signed Date')
    is_signed = fields.Boolean('Signed')
    signee_name = fields.Char('Signee')
    submit_deadline = fields.Date(string='Submit Deadline')
    note = fields.Text('Note')
    is_optional = fields.Boolean('Optional Submission')
    
    # Student doc
    student_doc_ids = fields.One2many('student.document', 'iu_doc_id', 'Submitted Documents')
    