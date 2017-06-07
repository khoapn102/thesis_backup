from openerp import models, fields, api

class StudentCourseAdditionWizard(models.TransientModel):

    _name = 'student.course.addition.wizard'
    _description = 'Add Students to Offering Courses'
    
    name = fields.Char(string='Name')
    offer_course_id = fields.Many2one('offer.course', string='Course')
    year_batch_id = fields.Many2one('year.batch', string='Year Batch')
    student_ids = fields.Many2many('student', string='Student Lists', compute='get_all_students_from_year_batch')
    
    @api.depends('year_batch_id')
    def get_all_students_from_year_batch(self):
        for record in self:
            if record.year_batch_id:
                all_students = self.env['student'].search([('academic_year_id.year_batch_id','=', record.year_batch_id.id)])
                print '=========', all_students
                if all_students:
                    record.student_ids = all_students.ids
    
    @api.multi
    def add_student_to_course(self):
        for record in self:
            if record.student_ids:
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
