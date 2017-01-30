from openerp import models, fields, api


class StudentTranscriptLine(models.Model):

    _name = 'student.transcript.line'
    _description = 'Student Transcript'

    course_id = fields.Many2one('course', string='Course Id')
    student_id = fields.Many2one('student', string='Student Id')
    gpa = fields.Float(string='GPA')
    credits = fields.Integer(
        string='No. of Credits', related='course_id.no_crds')
