## -*- coding: utf-8 -*-

from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _name = 'report.mrp.report_mrpbomstructure'
    _inherit = 'report.mrp.report_mrpbomstructure'

    def get_children(self, object, level=0):
        result = []
        
        def _get_rec(object, level):
            for l in object:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                qty_per_bom = l.bom_id.product_qty
                if uom:
                    if uom != l.bom_id.product_uom_id:
                        qty = uom._compute_quantity(qty, l.bom_id.product_uom_id)
                    res['pqty'] = (l.product_qty *qty)/ qty_per_bom
                else:
                    #for the first case, the ponderation is right
                    res['pqty'] = (l.product_qty *qty)
                res['puom'] = l.product_uom_id
                res['uname'] = l.product_uom.name
                res['level'] = level
                res['code'] = l.bom_id.code
                res['sale_delay'] = l.product_id.sale_delay
                res['qty_available'] = l.product_id.qty_available
                res['virtual_available'] = l.product_id.virtual_available
                res['free_stock'] = l.product_id.free_stock
                res['code'] = l.bom_id.code
                result.append(res)
                if l.child_line_ids:
                    if level < 6:
                        level += 1
                    _get_rec(l.child_line_ids, level, qty=res['pqty'], uom=res['puom'])
                    if level > 0 and level < 6:
                        level -= 1
            return result

        children = _get_rec(object,level)

        return children

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
