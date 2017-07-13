from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

class Semester(models.Model):
    
    _name = 'semester'
    _description = 'Semester'
    _order = 'semester_year, semester_type, id'
    
    name = fields.Char(string='Semester', compute='_get_semester_name_and_code',store=True)
    semester_year = fields.Char(string='Year',required=True,
                       default=(str(datetime.now().year) + '-' + str(datetime.now().year + 1)))
    semester_type = fields.Selection(selection=[('1', 'Semester 1'),
                                                ('2', 'Semester 2'),
                                                ('3', 'Semester 3')],
                                     string='Semester Type', required=True)
    semester_code = fields.Char(string='Semester Code',
                                compute='_get_semester_name_and_code', store=True)
    start_date = fields.Date(string='Starting Date', required=True,
                             default=datetime.now().strftime("%Y-%m-%d"))
    end_date = fields.Date(string='Ending Date', required=True,
                           default=datetime.now() + relativedelta(days=112))
    checkfield = fields.Char(string='Unique Field', default='Test')
    
    _sql_constraints = [('checkfield_unique', 'unique(checkfield)', 'There is existing Semester')]
    
    # List Offering courses in semester
    offer_course_ids = fields.One2many('offer.course', 'semester_id', string='Offering Courses')
    
    @api.onchange('semester_type','semester_year')
    def _onchange_semester_type(self):
        self.checkfield = self.semester_year + (self.semester_type or "")
        
#     @api.multi
#     def _get_semester_name(self):
#         for record in self:
#             record.name = record.semester_type + '-' + record.semester_year.split('-')[0]
#             
#     @api.multi
#     def _get_semester_code(self):
#         for record in self:
#             record.semester_code = record.semester_year.split('-')[0] + (record.semester_type or "")
    
    @api.depends('semester_year','semester_type')
    def _get_semester_name_and_code(self):
        for record in self:
            record.name = (record.semester_type or '') + '-' + record.semester_year.split('-')[0]
            record.semester_code = record.semester_year.split('-')[0] + (record.semester_type or "")
    
    @api.onchange('start_date')
    def _onchange_start_date(self):
        self.end_date = (datetime.strptime(self.start_date,'%Y-%m-%d') +\
                        relativedelta(days=112)).strftime('%Y-%m-%d')
    
    @api.constrains('start_date', 'end_date')
    def _validate_academic_year_period(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
    
    @api.multi
    def activate_calculate_gpa(self):
        for record in self:
            std_sem_ids = self.env['student.semester'].search([('semester_id','=',self.id)])
            for std_sem in std_sem_ids:
                if not std_sem.calculate_gpa:
                    std_sem.write({'calculate_gpa': True})
                else:
                    std_sem.write({'calculate_gpa': False})
                    
    @api.multi
    def update_student_financial_aid(self):
        for record in self:
            std_reg_ids = self.env['student.registration'].search([('semester_id','=',record.id)])
#             print '=====', std_reg_ids
            for std_reg in std_reg_ids:
                # Check if student has scholarship
                if std_reg.student_id.financial_aid_id:
                    # Check if scholarship still active or in period
                    student_id = std_reg.student_id
                    financial_aid_id = std_reg.student_id.financial_aid_id
                    std_financial_aid_id = self.env['student.financial.aid'].search([('student_id','=',student_id.id),
                                                                                      ('financial_aid_id','=',financial_aid_id.id)])
#                     print '======== HERE ', std_financial_aid_id
                    if std_financial_aid_id:
                        start = datetime.strptime(std_financial_aid_id.start_date,"%Y-%m-%d")
                        end = datetime.strptime(std_financial_aid_id.end_date,"%Y-%m-%d")
                        result = 0
                        if std_financial_aid_id.is_active and\
                            (start <= datetime.now() <= end):
                            if std_financial_aid_id.finance_type == 'percent':
                                result = std_reg.amount_tuition * std_financial_aid_id.finance_value/100
                            elif std_financial_aid_id.finance_type == 'amount':
                                result = std_financial_aid_id.finance_value
#                         print '==== NOW ', result
                        std_reg.write({'amount_financial_aid':result})
                                
                                  
            