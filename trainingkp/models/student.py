from openerp import models, fields, api


class Student(models.Model):

    _name = 'student'
    _order = 'id_number desc'
    _description = 'Student'

    name = fields.Char(string='Student Name', required=True)
    studentId = fields.Char(string='Student ID', required=True)
    id_number = fields.Char(string='Identify Number', required=True)
    gender = fields.Selection(
        selection=[('m', 'Male'), ('f', 'Female')], string='Gender')
    image = fields.Binary()
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    address = fields.Text(string='Address', required=True)
    phone = fields.Char(string='Phone Number')
    supervisor_id = fields.Many2one('lecturer', string='Supervisor ID')
    curr_gpa = fields.Float(string='Current GPA', compute='_compute_gpa')
    curr_classify = fields.Selection(string="Classification",
                                     selection=[('ex', 'Excellent'),
                                                ('vgd', 'Very Good'),
                                                ('gd', 'Good'),
                                                ('fgd', 'Faily Good'),
                                                ('f', 'Fair'),
                                                ('avg', 'Average'),
                                                ('wk', 'Weak'),
                                                ('rwk', 'Rather Weak'),
                                                ('twk', 'Too Weak')], compute='_classify_student')
    transcript_line_ids = fields.One2many(
        'student.transcript.line', 'student_id', string='Transcript Line IDs')
    # record set

    @api.multi
    def _compute_gpa(self):

        for student in self:
            gpa = 0.0
            crd = 0.0
            std_trans_line = student.transcript_line_ids
            for line in std_trans_line:
                gpa += (line.credits) * line.gpa
                crd += line.credits
            if crd != 0:
                gpa /= crd

            student.curr_gpa = gpa

    @api.multi
    def _classify_student(self):
        #         catez = {
        #             'ex': (85, 101),
        #             'vgd': (75, 85),
        #             'gd': (65, 75),
        #             'fgd': (60, 65),
        #             'f': (55, 60),
        #             'avg': (50, 55),
        #             'wk': (30, 50),
        #             'rwk': (10, 30),
        #             'twk': (0, 10)
        #         }
        #         for student in self:
        #             for x in catez:
        #                 if catez[x][0] <= student.curr_gpa < catez[x][1]:
        #                     student.curr_classify = x
        #                     break

        for student in self:
            # Reference another model
            res = self.env['gpa.classify'].search([
                ['score_start', '<=', student.curr_gpa],
                ['score_end', '>', student.curr_gpa]])
            for record in res:
                student.curr_classify = record.catez

    @api.multi
    def do_recompute(self):
        for x in self:
            x._compute_gpa()
        return True
