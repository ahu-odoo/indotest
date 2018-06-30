from openerp import models, fields, api

class product_product(models.Model):
    _inherit = "mrp.routing"

    location_dest_id = fields.Many2one('stock.location', 'Loc Output for MO\'s', help='Output location for manufacturing orders. Will simply be Stock if empty. Must be internal location',domain=[('usage','=','internal')])