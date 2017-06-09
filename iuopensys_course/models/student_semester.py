from openerp import models, fields, api

class StudentSemester(models.Model):
    
    _name = 'student.semester'
    _description = 'Student Semester'
    
    name = fields.Char(string='Name', default='Academic Semester')
    # General Info
    student_id = fields.Many2one('student', string = 'Student')
    user_id = fields.Many2one(related='student_id.user_id')
    semester_id = fields.Many2one('semester', string='Semester')
    
    # Student Course in semester
    student_course_ids = fields.Many2many('student.course',
                                         string='Study Courses in Semester',
                                         compute='get_student_course_in_semester')
    
    average_gpa = fields.Float(string='Semester Average GPA', compute='get_avg_gpa_semester')
    achieved_credits = fields.Integer(string='Achieved Credits', compute='get_avg_gpa_semester')
    total_credits = fields.Integer(string='Total Credits', compute='get_avg_gpa_semester')
    average_gpa_system_4 = fields.Float(string='Semester Average GPA (Sys. 4)')
    no_count_credits = fields.Integer(string='P/F Course Cred.',
                                    help='Credits that are not counted toward accumulated credits. Only determine Pass/Fail',
                                    compute='get_avg_gpa_semester')
    
    calculate_gpa = fields.Boolean(string='Caculate GPA')
    
    # Behavior Point
    academic_status = fields.Selection(string='Student Status',
                                      related='student_id.academic_status')
    learning_score = fields.Integer('Learning Score', default=0, help='GPA achieve >= 70')
    school_score = fields.Integer('School Score',default=0, help='Abide with School\'s Rules')
    social_score = fields.Integer('Social Score', default=0, help='Social Abilities')
    activity_score = fields.Integer('Activities Score', default=0,)
    leading_score = fields.Integer('Management Score', default=0,)
    discipline_score = fields.Integer('Discipline Score', default=0,)
    total_score = fields.Integer('Total Score', compute='get_total_score')
    
    @api.constrains('total_score')
    def validate_total_score(self):
        for record in self:
            if record.total_score > 100:
                raise ValueError('Total Score cannot be greater than 100')
    
    @api.depends('learning_score','school_score','social_score',\
                 'activity_score','leading_score','discipline_score')
    def get_total_score(self):
        for record in self:
            record.total_score = (record.learning_score + record.school_score +\
                                  record.social_score + record.activity_score +\
                                  record.leading_score) - record.discipline_score
                                  
    
    @api.depends('student_course_ids','calculate_gpa')
    def get_avg_gpa_semester(self):
        # Compute AVG = Sum(course_gpa * credit) / total_credits (no count pass/fail course)
        # 
        #
        for record in self:
            if record.student_course_ids and record.calculate_gpa:
                total_gpa = 0
                avg_gpa = 0
                total_cred = 0
                achieved_cred = 0
                no_count_cred = 0
                for std_crs in record.student_course_ids:
                    # Check if course_gpa is counted (normal)
                    if std_crs.offer_course_id.course_id.cred_count_type == 'count':
                        total_gpa += std_crs.course_gpa * std_crs.course_credits
                        achieved_cred += std_crs.course_credits
                        
                    elif std_crs.offer_course_id.course_id.cred_count_type == 'nocount':
                        no_count_cred += std_crs.course_credits
                    
                    total_cred += std_crs.course_credits
                   
                avg_gpa = total_gpa/achieved_cred
                                
                record.average_gpa = avg_gpa
                record.achieved_credits = achieved_cred
                record.total_credits = total_cred
                record.no_count_credits = no_count_cred                        

    @api.depends('student_id','semester_id')
    def get_student_course_in_semester(self):
        for record in self:
            if record.student_id and record.semester_id:
                temp = []
                std_crs_ids = self.env['student.course'].search([('student_id','=',record.student_id.id),
                                                                 ('semester_id','=',record.semester_id.id)])
                temp = std_crs_ids.ids
                for std_crs in std_crs_ids:
                    if std_crs.offer_course_id.is_lab == True or\
                        std_crs.offer_course_id.lab_type == 'combine':
                        temp.remove(std_crs.id)
                record.student_course_ids = temp
                