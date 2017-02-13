# -*- coding: utf-8 -*-

from openerp import models, api, fields
from openerp.exceptions import ValidationError

class Student(models.Model):
    
    _name = 'student'
    _inherits = {'res.users':'user_id'}
    _description = 'IU Student'
    
    # Fields
    user_id = fields.Many2one('res.users', string='User',
                              required=True, ondelete="cascade")        
    last_name = fields.Char(string='Last Name', size=128, required=True)
#     studentId = fields.Char(string='Student ID', size=15, compute='_get_studentId')
    studentId = fields.Char(string='Student ID', size=15,
                            default="Assigning")
    student_sequence = fields.Char('Student Sequence', size=5,
                                   default="Asgn")                                  
    academic_year_id = fields.Many2one('academic.year', string='Class')
    student_class_code = fields.Char(string='Student Class Code',
                                     compute='_get_student_class_code')
    gender = fields.Selection(selection=[('m', 'Male'), ('f', 'Female')],
                              string='Gender')
    birthdate = fields.Date(string='Birthdate')
    department_id = fields.Many2one('department', string='Department', required=True)                                    
    major_id = fields.Many2one('major', string='Major',
                               domain="[('department_id', '=', department_id)]",
                               required=True)
    country_id = fields.Many2one('res.country', string='Country',
                                 default=lambda self: self.env['res.country'].
                                 search([('id', '=', 243)]))
    ethnic = fields.Selection(selection=[('kinh', 'Kinh'),
                                         ('muong', 'Muong'),
                                         ('tay', 'Tay'),
                                         ('thai', 'Thai'),
                                         ('hmong', 'H\'Mong'),
                                         ('khome', 'Kho Me')], string='Ethnic')
    emergency_name = fields.Char(string='Emergency Contact Name', size=128)
    emergency_phone = fields.Char(string='Emergency Contact Phone', size=25)
    
    # Overide name_get to display Student Id rather than Name
    @api.multi
    def name_get(self):
        res = super(Student,self).name_get()
        data = []
        for record in self:
            val = ''
            val += record.studentId or ""
            val += ' - ' + record.last_name + ' ' + record.name
            data.append((record.id, val))
        return data 
    
    @api.multi
    def unlink(self):
        """
        Delete User when this record is deleted
        """
        for record in self:
            self.user_id.unlink()
            return super(Student, self).unlink()
    
    # Assign Student ID 
    @api.onchange('department_id')
    def _onchange_dept_id(self):
        if self.department_id:
            dept_code = 'student.'
            dept_code += str(self.department_id.dept_academic_code).lower()
            self.student_sequence = self.env['ir.sequence'].get(dept_code)
            

    @api.onchange('major_id','academic_year_id')
    def _onchange_dept_major_year_id(self):
        if self.major_id and self.academic_year_id:
           self.studentId = self.department_id.dept_academic_code +\
                            self.major_id.major_code +\
                            str(int(self.academic_year_id.year_batch_id.year)%100)+\
                            self.student_sequence
        else:
            self.studentId = self.student_sequence
        
    @api.multi
    def _get_student_class_code(self):
        for record in self: 
            if record.academic_year_id.id:           
                record.student_class_code = record.academic_year_id.class_code +\
                                            record.major_id.major_code
            else:
                raise ValidationError('Must input valid Academic year')
    
    @api.constrains('academic_year_id', 'major_id')
    def _check_validation_academic_year_for_student(self):
        for record in self:
            if record.academic_year_id.id and record.major_id.id:
                if record.academic_year_id.lecturer_id.department_id !=\
                    record.major_id.department_id:
                    raise ValidationError('Academic Advisor and Student must be in the same department')
            
    #Set Group Security for Student
    