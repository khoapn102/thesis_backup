from openerp import models, fields, api
from datetime import datetime

class Student(models.Model):
    
    _inherit = 'student'
    
    student_log_ids = fields.One2many('student.log', 'student_id', string='Logs')
    
    
#     @api.model
#     def create(self, vals):
#         curr_student = super(Student, self).create(vals)
        
    @api.multi
    def write(self, vals):
        """
        1. If any field is updated for student
        2. -> will write to log file both old and new value
        3. -> determine base on 
        """
        for record in self:
            if vals:
                model_map = { 'department_id': ('Department','department', record.department_id.name),
                              'major_id': ('Major', 'major', record.major_id.name),
                              'std_academic_prog_id': ('Academic Program', 'student.academic.program', record.std_academic_prog_id.name),
                              'academic_year_id': ('Class', 'academic.year', record.academic_year_id.name),
                              'year_batch_id': ('Batch', 'year.batch', record.year_batch_id.name),
                              'financial_aid_id': ('Financial Aid', 'financial.aid', record.financial_aid_id.name),}
                
                # Selection Field
                academic_status = dict(self.env['student']._columns['academic_status'].selection)
                
                no_model_map = {
                                'academic_status': ('Academic Status',academic_status[record.academic_status]),
                                'studentId': ('Student ID', record.studentId)
                                }
                for item in vals:
                    if item in model_map or no_model_map:
                        field_change = item
                        student_id = record.id
                        modified_user_id = self.env.user.id
                        modified_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        field_change_name = ''
                        old_value = ''
                        new_value = ''
                        
                        # For Model Mapping
                        if item in model_map:
                            field_change_name = model_map[item][0]
                            old_value = model_map[item][2]
                            model = model_map[item][1]
                            model_id = self.env[model].search([('id','=',vals[item])])
                            if model_id:
                                new_value = model_id.name
                        
                        # For none model Mapping- values, integer, selection, float ..                  
                        elif item in no_model_map:
                            field_change_name = no_model_map[item][0]
                            old_value = no_model_map[item][1]
                            if item == 'academic_status':
                                new_value = academic_status[vals[item]]
                            else:
                                new_value = vals[item]
                            
                        new_vals = {'student_id':student_id,
                                    'modified_user_id': modified_user_id,
                                    'field_change': field_change,
                                    'field_change_name': field_change_name,
                                    'modified_date': modified_date,
                                    'old_value':old_value,
                                    'new_value':new_value,
                                    }
#                         print '=======', new_vals
                        self.env['student.log'].create(new_vals)
                        
        return super(Student,self).write(vals)        
                        
                        
                        
                        
                        
                        
                        
                   
                   
                    