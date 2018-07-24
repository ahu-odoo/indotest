from odoo import api, fields, models, _

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('compute_from_project_qty')
    def product_id_change_with_wh(self):
        pqty = self.order_id.project_qty
        if pqty>0:
        	self.price_unit = self.order_id.pricelist_id.price_get(product, pqty)[pricelist]
        self.customer_lead = self.product_id.sale_delay
