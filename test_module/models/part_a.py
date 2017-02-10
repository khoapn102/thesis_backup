from openerp import models, fields, api

class PartA(models.Model):
    
    _name = 'part.a'
    _description = 'Test A'
    
    name = fields.Char('Name')
    test_change = fields.Selection(selection=[('1','1'),
                                              ('2','2'),
                                              ('3','3')], string='Test Change')
    part_b_ids = fields.One2many('part.b','part_a_id', 'Part Bs')
    
    @api.onchange('test_change')
    def _onchange_test_change(self):
        res = []
        b_ids = None
        if self.test_change:
            b_ids = self.env['part.b'].search_read([('part_a_id','=',int(self.test_change))])
        print '++++++++++', b_ids
        if b_ids:
            for item in b_ids:
                res.append((0,0,item))
            result = {'value':{'part_b_ids':res}}
            print '--------', res
            return result