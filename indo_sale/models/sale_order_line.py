from odoo import api, fields, models, _

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('compute_from_project_qty')
    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):
        res = super(sale_order_line, self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty=qty,uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, warehouse_id=warehouse_id, context=context)
        order_id = self.pool.get('sale.order.line').browse(cr,uid,ids).order_id
        if context.get('project_qty',False):
        	pqty = context.get('project_qty')
	        if pqty != 0:
	        	pricelist_obj = self.pool.get('product.pricelist')
	        	price = pricelist_obj.price_get(cr,uid,ids,product, pqty)[pricelist]
	        	res['value']['price_unit'] = price
        return res
