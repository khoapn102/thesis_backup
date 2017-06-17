from openerp import models, fields, api

class StudentBalanceUpdateWizard(models.TransientModel):
    
    _name = 'student.balance.update.wizard'
    _description = 'Update Student Balance'
    
    student_id = fields.Many2one('student')
    student_balance = fields.Float('Balance')
    tuition_discount = fields.Boolean('Instant Discount Apply',
                                      help="Only when student balance has money, opt will show up.\
                                                     Depends on amount of cash, student can receive the discount rate 10%")
   
    @api.multi
    def update_balance(self):
        for record in self:
            if record.student_id:
                curr_bal = record.student_id.student_balance
                curr_bal += record.student_balance
#                 tuition_limit = record.student_id.major_id.std_academic_prog_id.tuition_at_iu
                new_vals={'student_balance':curr_bal}
                if record.tuition_discount:
                    discount_time = record.student_id.tuition_discount_time + 1
                    new_vals['tuition_discount_time'] = discount_time
                student = self.env['student'].search([('id','=',record.student_id.id)])
                student.write(new_vals)
                return True
                    