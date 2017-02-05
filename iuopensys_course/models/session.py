from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Session(models.Model):
    
    _name = 'session'
    _description = 'Course Session'
    
    name = fields.Char('Session Name', size=16, required=True,
                       default="Session 1")
    offer_course_id = fields.Many2one('offer.course', string='Course')
    start_date = fields.Date(string='Start Date',
                                    default = datetime.now().strftime("%Y-%m-%d"))
    end_date = fields.Date(string='End Date',
                                  default=datetime.now() + relativedelta(days=102))
    start_time = fields.Float(string='Start Time', required=True)
#     hour = fields.Selection(
#         [('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
#          ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
#          ('16', '16'), ('17', '17'),], 'Starting Hour', required=True,
#                             default='8')
#     minute = fields.Selection(
#         [('00', '00'), ('15', '15'), ('30', '30'), ('45', '45')], 'Minute',
#         required=True, default='00')
    duration = fields.Float('Duration', required=True)
    is_summer = fields.Boolean(string='Summer Session')
#     display_hour = fields.Char(string='Recording Hour',
#                                 compute='_get_display_hour')
#     display_duration = fields.Char(string='Recording Duration',
#                                    compute='_get_display_duration')
#     
#     @api.multi
#     def _get_display_hour(self):
#         for record in self:
#             record.display_hour = record.hour + ':' + record.minute
#             
#     @api.multi
#     def _get_display_duration(self):
#         for record in self:
#             hr = int(record.duration)
#             minute = int((record.duration - hr)*60)
#             if hr:
#                 record.display_duration = str(hr) + ' hours and ' +\
#                                              str(minute) + ' minutes'
#             else:
#                 record.display_duration = str(minute) + ' minutes'
    