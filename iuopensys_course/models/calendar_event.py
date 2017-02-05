from openerp import models, fields, api

class CalendarEvent(models.Model):
    
    _inherit = 'calendar.event'
    
    offer_course_id = fields.Many2one('offer.course', string='Course')
    
    
#     @api.onchange('offer_course_id')
#     def _onchange_offer_course(self):
#         if self.offer_course_id:
#             self.
    