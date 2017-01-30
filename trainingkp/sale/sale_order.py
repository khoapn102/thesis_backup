from openerp import models, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def button_print_sale_order(self):
        print '-------------- clicked'
        report_name = 'trainingkp.report_sale_custom_template'
        return self.env['report'].get_action(self, report_name)
