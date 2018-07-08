from odoo import api, fields, models, _


class stock_quant(osv.osv):
    _inherit = "stock.quant"
    
    def quants_get_preferred_domain(self, qty, move, ops=False, lot_id=False, domain=None, preferred_domain_list=[]):
        if context.get('from_indo_stock_only',False):
            prefered_domain_list=[[('location_id','=',12),('qty','>',0),('propagated_from_id','=',False)]]
        else:
            prefered_domain_list=[]
        return super(stock_quant, self).quants_get_preferred_domain(qty, move, ops=False, lot_id=False, domain=None, prefered_domain_list=prefered_domain_list)

class stock_picking(osv.osv):
    _inherit = "stock.picking"


    def create(self, values):    
        picking = super(stock_picking, self).create(values)
        if picking.group_id:
            sale_ids = sale_obj.search([('procurement_group_id', '=', picking_rec.group_id.id),('user_id','!=',False)])
            if sale_ids:
                picking_rec.message_subscribe_users(user_ids=[sale_ids[0].user_id.id])                
        return picking

    def write(self,values):    
        picking_rec = super(stock_picking, self).write(values)

        if picking_rec.group_id:
            sale_ids = sale_obj.search([('procurement_group_id', '=', picking_rec.group_id.id),('user_id','!=',False)])
            if sale_ids:
                picking_rec.message_subscribe_users(user_ids=[sale_ids[0].user_id.id])  
        return picking_rec