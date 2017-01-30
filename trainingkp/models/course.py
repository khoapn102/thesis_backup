from openerp import models, fields, api


class Course(models.Model):

    _name = 'course'  # file name, class name, model name same
    _description = 'Course'

    name = fields.Char('Course Name', required=True)
    courseId = fields.Char('Course ID', required=True)
    no_crds = fields.Integer('No. of Credits', required=True)
    lecturer_ids = fields.Many2many('lecturer')
    no_students = fields.Integer('Number of Students', required=True)
