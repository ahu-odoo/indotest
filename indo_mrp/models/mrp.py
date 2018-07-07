import time

import odoo.addons.decimal_precision as dp
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _
from odoo import tools, SUPERUSER_ID
from odoo.addons.product import _common

class mrp_production(models.Model):
    _inherit='mrp.production'

    #ahu-migration note:
    #this function doens't exist anymore in standard, so won't be called. But need to check later if necessary for Indo
    def _make_consume_line_from_data(self, cr, uid, production, product, uom_id, qty, uos_id, uos_qty, context=None):
        stock_move = self.env['stock.move']
        loc_obj = self.env['stock.location']
        proc_obj = self.env['procurement.group']
        # Internal shipment is created for Stockable and Consumer Products
        if product.type not in ('product', 'consu'):
            return False
        # Take routing location as a Source Location.
        source_location_id = production.location_src_id.id
        prod_location_id = source_location_id
        prev_move= False
        if production.bom_id.routing_id and production.bom_id.routing_id.location_id and production.bom_id.routing_id.location_id.id != source_location_id:
            source_location_id = production.bom_id.routing_id.location_id.id
            prev_move = True
        if len(proc_obj.search([('name','=',production.name)])) < 1:
            proc_rec = proc_obj.create({'name':production.name,'move_type':'direct'})
        else:
            proc_rec = proc_obj.search([('name','=',production.name)])[0]

        destination_location_id = production.product_id.property_stock_production.id
        move_id = stock_move.create(cr, uid, {
            'name': production.name,
            'date': production.date_planned,
            'date_expected': production.date_planned,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': uom_id,
            'product_uos_qty': uos_id and uos_qty or False,
            'product_uos': uos_id or False,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'company_id': production.company_id.id,
            'procure_method': prev_move and 'make_to_stock' or self._get_raw_material_procure_method(cr, uid, product, location_id=source_location_id,
                                                                                                     location_dest_id=destination_location_id, context=context), #Make_to_stock avoids creating procurement
            'raw_material_production_id': production.id,
            #this saves us a browse in create()
            'price_unit': product.standard_price,
            'origin': production.name,
            'warehouse_id': loc_obj.get_warehouse(cr, uid, production.location_src_id, context=context),
            'group_id': production.move_prod_id.group_id.id or proc_rec,
        }, context=context)
        
        if prev_move:
            prev_move = self._create_previous_move(cr, uid, move_id, product, prod_location_id, source_location_id, context=context)
            stock_move.action_confirm(cr, uid, [prev_move], context=context)
        return move_id

    #ahu-migration note:
    #was done earlier in order to cancel all related moves when cancelling mrp.production. Need to check if v10 solves this in standard.
    #uncommenting first and let's see how standard feature behave in accordance with Indo
    # def action_cancel(self, cr, uid, ids, context=None):
    #     super(mrp_production, self).action_cancel(cr, uid, ids, context=context)
    #     if context is None:
    #         context = {}
    #     move_obj = self.pool.get('stock.move')
    #     proc_obj = self.pool.get('procurement.order')
    #     procgroup_obj = self.pool.get('procurement.group')
    #     pick_obj = self.pool.get('stock.picking')
    #     for production in self.browse(cr, uid, ids, context=context):
    #         group = procgroup_obj.search(cr, uid, [('name', '=', production.name)], context=context)
    #         if group:
    #             move_records = move_obj.search(cr, uid, [('group_id', '=', group[0]),('state','not in', ['done','cancel'])])
    #             if move_records:
    #                 for recs in move_records:
    #                     #hack: has to remove move_dest_id otherwise trying to remove that move dest
    #                     move_obj.write( recs, {'move_dest_id':False})
    #                     move_obj.action_cancel(cr, uid, recs, context=context)
    #     return True

    def create(self, cr, uid, values, context=None):
        if values.get('routing_id',False):
            routing = self.pool.get('mrp.routing').browse(values.get('routing_id'))
            if routing.location_dest_id:
                values['location_dest_id']=routing.location_dest_id.id
        res = super(mrp_production, self).create(values,context=context)
        group = self.pool.get('ir.model.data').xmlid_to_object('indo_sale.auto_add_mo')
        self.message_subscribe_users([res],user_ids=group.users.ids)
        return res

    # Should be left out in next version
    def on_change_date_planned(self, cr, uid, ids, date_planned, context=None):
        """ 
        Changing date planned on an MO should change the date of a 
        """
        for record in self:
            if record.move_created_ids:
                for line in record.move_created_ids:
                    line.write({'date_expected':date_planned})