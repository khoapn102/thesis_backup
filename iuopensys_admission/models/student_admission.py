from openerp import models, fields, api
import xlrd

class StudentAdmission(models.Model):
    
    _name = 'student.admission'
    _description = 'Student Admission'
    
    exel_file = fields.Binary(string='Excel File')