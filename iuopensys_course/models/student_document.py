from openerp import models, fields, api

class ir_attachment(models.Model):
    
    _inherit = 'ir.attachment'
    
    student_document_id = fields.Many2one('student.document', 'Student Document')

class StudentDocument(models.Model):
    
    _name = 'student.document'
    _description = 'Student Document Relation'
    
    # Student
    student_id = fields.Many2one('student', 'Student')
    
    # document
    iu_doc_id = fields.Many2one('iu.document', 'Document Name')
    submit_deadline = fields.Date(related='iu_doc_id.submit_deadline')
    
    # attachment
    attachment_ids = fields.One2many('ir.attachment', 'student_document_id', string='Attachments')
    is_stored = fields.Boolean(string='Stored Copy')
    is_submit = fields.Boolean(string='Submitted')
    
    @api.onchange('attachment_ids')
    def onchange_attachment(self):
        for record in self:
            if record.attachment_ids:
                record.is_stored = True
                if not record.is_submit:
                    record.is_submit = True
            else:
                record.is_stored = False
    
    