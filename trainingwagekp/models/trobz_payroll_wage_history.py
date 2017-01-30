from openerp import models, fields, api
from datetime import datetime
from dateutil import relativedelta


class TrobzPayrollWageHistory(models.Model):

    _name = 'trobz.payroll.wage.history'
    _order = 'effective_date desc, id desc'
    _description = 'Payroll Wage History'

    name = fields.Char(string='Revision No', size=20, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True, readonly=True)
    contract_id = fields.Many2one(
        'hr.contract', string='Contract', readonly=True)
    department_id = fields.Many2one(
        'hr.department', string='Department', readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Title', readonly=True)
    pre_wage = fields.Float(
        string='Previous Wage', required=True, readonly=True)
    cur_wage = fields.Float(
        string='Current Wage', required=True, readonly=True)
    difference = fields.Float(string='Difference',
                              compute='_compute_wage_diff', store=True)
    percentage = fields.Float(string='Percentage',
                              compute='_compute_percentage', store=True)
    effective_date = fields.Date(string='Effective Date', required=True,
                                 default=fields.Date.today())
    responsible_id = fields.Many2one(
        'res.partner', string='Responsible Manager', readonly=True)
    eff_month = fields.Char(string="Effective Month",
                            compute='_get_month_year', store=True)
    eff_year = fields.Char(string="Effective Year",
                           compute="_get_month_year", store=True)
    until_eff_date = fields.Integer(string='Months until Effective Date',
                                    compute='_get_months_until_eff_date')
    state = fields.Selection(string='State',
                             selection=[('ok', 'OK'),
                                        ('cancel', 'Cancel')],
                             default='cancel')
#     order_by = fields.Char(string='Order By', compute='_get_order')
#
#     def _get_order(self):
#         self.order_by = self.env['trobz.payroll.wage.history.report'].order_by

    def _get_months_until_eff_date(self):
        for x in self:
            format = '%Y-%m-%d'
            #             m = int(datetime.strptime(x.effective_date, format).month)
            #             temp_date = datetime.now() + relativedelta(months=-m)
            x.until_eff_date = int(
                (relativedelta.relativedelta(datetime.now(),
                                             datetime.strptime(x.effective_date, format))).months)

    @api.depends('pre_wage', 'cur_wage')
    def _compute_wage_diff(self):
        """
            Compute Wage Difference
        """
        for x in self:
            x.difference = x.cur_wage - x.pre_wage
            if x.difference < 0:
                raise Warning('Current Wage must larger than Previous Wage')

    @api.depends('pre_wage', 'cur_wage')
    def _compute_percentage(self):
        """
            Compute Percentage
        """
        for x in self:
            x.percentage = x.pre_wage > 0 and 100 * \
                (x.cur_wage - x.pre_wage) / x.pre_wage or 0

    def _get_month_year(self):
        """
            Compute Effective Month and Year for Filter
        """
        for x in self:
            x.eff_month = str(
                datetime.strptime(x.effective_date, '%Y-%m-%d').month)
            x.eff_year = str(strptime(x.effective_date, '%Y-%m-%d').year)

    @api.model
    def search(self, args, offset=0, limit=None, order='effective_date DESC', count=False):
        """
            Overide Search Method
            This is the core of displaying the Record 
            and setting up Context
        """
        context = self._context
        results = []
        # Filter for Highest Raise in 12 months
        if context.get('filter_highest_raise', False):
            self._cr.execute("""SELECT id FROM trobz_payroll_wage_history
                     WHERE difference IN
                     (SELECT MAX(difference)
                     FROM trobz_payroll_wage_history
                     WHERE pre_wage > 0 
                     AND effective_date >= (CURRENT_DATE - INTERVAL '12 MONTH'))""")
            record_ids = self._cr.fetchall()

            for record in record_ids:
                results.append(record[0])
            args.append(('id', 'in', results))
        # Filter for No Raise Salary in 12 months
        if context.get('filter_no_raise', False):
            self._cr.execute("""SELECT id FROM trobz_payroll_wage_history
                    WHERE difference = 0
                    AND effective_date >= (CURRENT_DATE - INTERVAL '12 MONTH')""")
            record_ids = self._cr.fetchall()

            for record in record_ids:
                results.append(record[0])
            args.append(('id', 'in', results))

        if context.get('order_by', False):
            order = context.get('order_by')

        return super(TrobzPayrollWageHistory, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
