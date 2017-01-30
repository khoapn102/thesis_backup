from openerp import models, fields, api

class OfferCourse(models.Model):
    
    _name = 'offer.course'
    _description = 'Offered Course in Semester'
    
    name = fields.Char(string='Course Name')
    course_id = fields.Many2one('course', string='Parent Course')
    course_code = fields.Char(string='Course Code', size=10,
                              compute='_generate_course_code')
    course_group = fields.Selection(selection=[('grp1', 'Group 1'),
                                               ('grp2', 'Group 2'),
                                               ('grp3', 'Group 3'),
                                               ('grp4', 'Group 4'),
                                               ('grp5', 'Group 5'),
                                               ('grp6', 'Group 6'),
                                               ('grp7', 'Group 7')],
                                    string='Course Group',
                                    help='Group of Courses')
    department_id = fields.Many2one('department', string='Department',
                                    related='course_id.department_id')
    numb_students = fields.Integer(string='Number of Students',
                                   help='Maximum number of students for each offered course')
    # Compute here
    curr_enroll_students = fields.Integer(string='Current Number of Students',
                                        default=0)
    
    assign_room = fields.Char(string='Assigned Room')
    is_lab = fields.Boolean(string='Active Lab')
    lab_type = fields.Selection(selection=[('separate', 'Separate'),
                                           ('combine', 'Combine')],
                                string='Lab Type',
                                help='Determine if the lab is grouped with theory class or is separated')
    academic_year_id = fields.Many2one('academic.year', string='Class')
    semester_id = fields.Many2one('semester', string='Semester')
    lecturer_id = fields.Many2one('lecturer', string='Lecturer')
    
    # Student List
    student_course_ids = fields.One2many('student.course', 'offer_course_id',
                                         string='Students')
    
    # Grade and Trancsript
    mid_exam_percent = fields.Integer(string='Midterm Exam Percentage', default=0)
    final_exam_percent = fields.Integer(string='Final Exam Percentage', default=0)
    
    
    # PERIOD, EXAM SCHEDULE and TIME SCHEDULE go here
    
    # Overide name_get
    @api.multi
    def name_get(self):
        res = super(OfferCourse,self).name_get()
        data = []
        
        for record in self:
            val = ''
            val += record.course_code or ""
            val += ' - ' + record.name
            data.append((record.id, val))
        return data
    
    # If the course is lab, other attributes will be changed
    @api.onchange('is_lab')
    def _onchange_is_lab(self):
        if self.is_lab:
            self.name += ' Lab'
        else:
            self.name = self.course_id.name            
    
    # Unique Course Code
    def _generate_str_id(self, id):
        if id >= 1 and id <= 9:
            return '00' + str(id)
        elif id >= 10 and id <= 99:
            return '0' + str(id)
        else:
            return str(id)
        
    @api.multi
    def _generate_course_code(self):
        for record in self:
            record.course_code = record.department_id.dept_academic_code +\
                                 record._generate_str_id(record.id) + 'IU'