from openerp import models, fields, api

class CalendarEvent(models.Model):
    
    _inherit = 'calendar.event'
    
    study_period_id = fields.Many2one('study.period', string='Study Period', ondelete='cascade')
    offer_course_id = fields.Many2one('Course', related='study_period_id.offer_course_id')
    
#     @api.onchange('offer_course_id')
#     def _onchange_offer_course_id(self):
#         for record in self:
#             if record.offer_course_id:
#                 record.name = record.offer_course_id.name + ' - ' + record.session_name

    