from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning

class StudentCourseAdditionWizard(models.TransientModel):

    _name = 'student.course.addition.wizard'
    _description = 'Add Students to Offering Courses'
    
    name = fields.Char(string='Name')
    offer_course_id = fields.Many2one('offer.course', string='Course')
    has_lab = fields.Boolean(related='offer_course_id.has_lab')
    lab_course_ids = fields.Many2many('offer.course',string='Lab Courses')
    
    year_batch_id = fields.Many2one('year.batch', string='Year Batch')
    student_ids = fields.Many2many('student', string='Student Lists', compute='get_all_students_from_year_batch')
    
    student_id = fields.Many2one('student', string='Student')
    
    @api.depends('year_batch_id')
    def get_all_students_from_year_batch(self):
        for record in self:
            if record.year_batch_id:
                all_students = self.env['student'].search([('academic_year_id.year_batch_id','=', record.year_batch_id.id)])
#                 print '=========', all_students
                if all_students:
                    record.student_ids = all_students.ids
    
    @api.multi
    def add_student_to_course(self):
        for record in self:
            # Only add student for Extra-curricluar (in batch) -> check for course
            if record.student_ids and record.offer_course_id.course_id.is_extra_curricular:
                # Search the course see if students have been added
                for student in record.student_ids:
                    check_std_crs_id = self.env['student.course'].search([('student_id','=', student.id),
                                                                          ('offer_course_id','=',record.offer_course_id.id)])
                    if check_std_crs_id:
                        continue
                    # If student has not been added -> create student_course
                    new_vals = {
                                'student_id': student.id,
                                'offer_course_id':record.offer_course_id.id,
                                }
                    student_course = self.env['student.course']
                    student_course.create(new_vals)
            elif not record.offer_course_id.course_id.is_extra_curricular:
                raise ValidationError('Please check if registered course is Extra-curricular Course.')

    # Manually register Student to course w/wo lab
    @api.multi
    def add_a_student_to_course(self):
        for record in self:
            if record.student_id:
                # Find Student Registration
                std_reg_id = self.env['student.registration'].search([('student_id','=',record.student_id.id),
                                                                        ('semester_id','=',record.offer_course_id.semester_id.id)])
                if std_reg_id:
                    # Has Lab
                    if record.has_lab:
                        if record.lab_course_ids:
                            lab_ids = std_reg_id.offer_course_ids.ids
                            for lab in record.lab_course_ids:
                                lab_ids.append(lab.id)
                            new_vals = {'offer_course_ids': [(6,0,lab_ids)]}
                        else:
                            raise ValidationError('Please register Lab Course for student.')
                    # No lab
                    else:
                        new_crs_ids = std_reg_id.offer_course_ids.ids
                        new_crs_ids.append(record.offer_course_id.id)
                        new_vals = {'offer_course_ids': [(6,0,new_crs_ids)]}
                        
                    std_reg_id.write(new_vals)
                    
                
                                          