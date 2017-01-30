from openerp.report import report_sxw
from openerp.osv import osv
import contextlib


class sale_common(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_common, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'concat_so_customer': self.concat_so_customer})

    def concat_so_customer(self, o):
        return '%s- %s' % (o.name, partner_id.name)


class sale_custom(osv.AbstractModel):
    _name = 'report.trainingkp.report_sale_custom_template'
    _inherit = 'report.abstract_report'
    _template = 'trainingkp.report_sale_custom_template'
    _wrapped_report_class = sale_common
