from openerp import models, fields, api


class HrContract(models.Model):

    _inherit = 'hr.contract'

    @api.model
    def create(self, vals):
        """
            Create Contract then create Wage History
            Passing Id of the Many2one fields to retrieve its name
            Write value of Many2one using format {'field_id':id}
        """
        cur_contract = super(HrContract, self).create(vals)
        new_vals = {'name': 'Wage History',
                    'employee_id': cur_contract.employee_id.id,
                    'department_id': cur_contract.department_id.id,
                    'contract_id': cur_contract.id,
                    'job_id': cur_contract.job_id.id,
                    'responsible_id': self.env.user.id,
                    'pre_wage': 0,
                    'cur_wage': cur_contract.wage,
                    'effective_date': fields.Date.today(),
                    }
        self.env['trobz.payroll.wage.history'].create(new_vals)
        return cur_contract

    @api.multi
    def write(self, vals):
        """
            Update Contract -> Update Wage history with the current employee,
            1. Search for the newest Wage History on that Employee,
            2. Change and Update
        """
        for contract in self:
            if 'wage' in vals:
                #                 wage_hist = self.env['trobz.payroll.wage.history'].search(
                #                     [('employee_id', '=', contract.employee_id.id),
                #                      ('contract_id', '=', contract.id)],
                # order='id desc, effective_date desc', limit=1)
                new_vals = {'name': 'Promotion',
                            'employee_id': contract.employee_id.id,
                            'department_id': contract.department_id.id,
                            'contract_id': contract.id,
                            'job_id': contract.job_id.id,
                            'responsible_id': self.env.user.id,
                            'pre_wage': contract.wage,
                            # value of changed fields
                            'cur_wage': vals['wage'],
                            'effective_date': fields.Date.today(),
                            }
                self.env['trobz.payroll.wage.history'].create(new_vals)
        return super(HrContract, self).write(vals)
