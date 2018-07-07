from odoo import api, fields, models, _

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('compute_from_project_qty')
    def product_id_change_with_wh(self):
        if context.get('project_qty',False):
        	pqty = context.get('project_qty')
	        if pqty != 0:
	        	price = self.order_id.pricelist_id.price_get(product, pqty)[pricelist]
	        	self.price_unit = price
        self.customer_lead = self.product_id.sale_delay
