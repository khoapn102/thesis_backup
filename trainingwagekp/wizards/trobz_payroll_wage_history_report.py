from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TrobzPayrollWageHistoryReport(models.TransientModel):

    _name = 'trobz.payroll.wage.history.report'
    _description = 'Trobz Payroll Wage History Report'

    to_date = fields.Date(string='To Date', default=fields.Date.today())
    from_date = fields.Date(string='From Date',
                            default=lambda g:
                            (datetime.now() +
                             relativedelta(months=-12)).strftime('%Y-%m-%d'))
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job Title')
    # for one or many Employees
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    order_by = fields.Selection(string='Order By',
                                selection=[('effective_date DESC',
                                            'Effective Date Descending'),
                                           ('cur_wage DESC',
                                            'Current Wage Descending'),
                                           ('percentage DESC',
                                            'Percentage Descending'),
                                           ],
                                default='cur_wage DESC')

    @api.multi
    def get_print_report(self):
        domain = [('effective_date', '>=', self.from_date),
                  ('effective_date', '<=', self.to_date),
                  ('employee_id', 'in', self.employee_ids.ids),
                  ('department_id', '=', self.department_id.id),
                  ('job_id', '=', self.job_id.id)]
        for report in self:
            """
                context is frozendict -> skip_invert = False to insert new Val
            """
            list_view = self.env.ref(
                'trainingwagekp.payroll_wage_hist_wizard_tree_view')
            self.env.context = self.with_context(skip_invert=False).env.context
            context = self._context.copy()
            if not context:
                context = {}
    #       Passing context value for Return Action window
            context.update({'group_by': ['department_id', 'job_id'],
                            'order_by': report.order_by})

    #         recordset = self.with_context(context)

            action = {'name': 'Wage History Report',
                      'type': 'ir.actions.act_window',
                      'view_type': 'form',
                      'view_mode': 'tree',
                      'view_id': list_view.id,
                      'res_model': 'trobz.payroll.wage.history',
                      'context': context,
                      'domain': domain,
                      }
            return action
