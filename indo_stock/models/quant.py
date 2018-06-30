from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging


class stock_quant(osv.osv):
    _inherit = "stock.quant"
    
    def quants_get_prefered_domain(self, cr, uid, location, product, qty, domain=None, prefered_domain_list=[], restrict_lot_id=False, restrict_partner_id=False, context=None):
        if context.get('from_indo_stock_only',False):
            prefered_domain_list=[[('location_id','=',12),('qty','>',0),('propagated_from_id','=',False)]]
        else:
            prefered_domain_list=[]
        return super(stock_quant, self).quants_get_prefered_domain(cr, uid, location, product, qty, domain=None, prefered_domain_list=prefered_domain_list, restrict_lot_id=False, restrict_partner_id=False,context=context)

class stock_picking(osv.osv):
    _inherit = "stock.picking"


    def create(self, cr, uid, values, context=None):    
        picking = super(stock_picking, self).create(cr,uid,values,context=context)
        picking_rec = self.browse(cr,uid,picking)
        sale_obj = self.pool.get("sale.order")
        if picking_rec.group_id:
            sale_ids = sale_obj.search(cr, uid, [('procurement_group_id', '=', picking_rec.group_id.id),('user_id','!=',False)], context=context)
            if sale_ids:
                sale_rec=sale_obj.browse(cr,uid,sale_ids[0])
                picking_rec.message_subscribe_users(user_ids=[sale_rec[0].user_id.id])                
        return  picking

    def write(self, cr, uid, ids, values, context=None):    
        sale_obj = self.pool.get("sale.order")
        write_res = super(stock_picking, self).write(cr, uid, ids, values, context=context)
        picking_rec = self.browse(cr,uid,ids)

        if picking_rec.group_id:
            sale_ids = sale_obj.search(cr, uid, [('procurement_group_id', '=', picking_rec.group_id.id),('user_id','!=',False)], context=context)
            if sale_ids:
                sale_rec=sale_obj.browse(cr,uid,sale_ids[0])
                picking_rec.message_subscribe_users(user_ids=[sale_rec[0].user_id.id])  
        return write_res