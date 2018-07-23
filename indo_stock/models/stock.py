from datetime import datetime, date, time
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class ProductForecast(models.Model):
    _name = "product.forecast"
    _order = "date ASC"

    name = fields.Many2one('product.product',string="Product", required=True)
    date = fields.Date("Date")
    qty = fields.Float("Quantity")
    total_qty = fields.Float("Total Quantity")
    stock_treshold = fields.Float(related="name.stock_treshold",string='Threshold',store=True)
    picking_id = fields.Many2one('stock.picking','Picking')
    overdue = fields.Boolean('Overdue')
    origin = fields.Char('Origin')


class product_product(models.Model):
    _inherit = "product.product"
    
    stock_level_ids = fields.One2many('product.forecast','name','Stock Levels')
    stock_treshold = fields.Float('Stock Threshold', default=0.0)
    # stock_insufficient = fields.Boolean(compute='_is_stock_insufficient', string='Is stock insufficient?',store=True)
    stock_insufficient = fields.Boolean(string='Is stock insufficient?', readonly=True)
    free_stock = fields.Float(compute='_compute_free_stock', readonly=True)

    # @api.one
    # @api.depends('stock_treshold','stock_level_ids')
    # def _is_stock_insufficient(self):
    #     self.stock_insufficient = False
    #     treshold = self.stock_treshold
    #     for rec in self.stock_level_ids:
    #         if rec.total_qty < treshold:
    #             self.stock_insufficient = True

    @api.one
    @api.depends('qty_available','outgoing_qty')
    def _compute_free_stock(self):
        self.free_stock = self.qty_available - self.outgoing_qty

    @api.model
    def _process_compute_forecast(self):
        #selection is based on the two different sets:
        #   - first: all the stock.moves products not yet in Done status
        #   - second: all the products that already had at least some lines in their forecasts.
        #             for that second part, we only filter on the one's having a picking_id because those are the only
        #             ones needed 
        # Done in SQL as not subject to access rights and this is much faster
        # import ipdb; ipdb.set_trace()
        self.env.cr.execute('''
                    SELECT product_id 
                    from stock_move
                    WHERE write_date > NOW() - INTERVAL '30 days' OR create_date > NOW() - INTERVAL '30 days'
                   ''')
        for prod_id in self.env.cr.fetchall():
            if prod_id != False:
                self.search([('id','=',prod_id[0])]).compute_forecasts()


    @api.onchange('stock_treshold')
    def onchange_stock_treshold(self):
        threshold = self.stock_treshold
        self.stock_insufficient = False
        for item in self.stock_level_ids:
            if item.total_qty < threshold:
                self.stock_insufficient = True
                break

    @api.one
    def compute_forecasts(self,context=None):
        treshold = self.stock_treshold
        if context is None:
            context = {}
        product_ids = self.id
        if 'location_id' in context:
            location_id = context['location_id']
        else:
            warehouse_id = self.env['stock.warehouse'].search([])[0].id
            location_id = self.env['stock.warehouse'].browse(warehouse_id).lot_stock_id.id
        loc_ids = self.env['stock.location'].search([('location_id','child_of',[location_id])]).ids
        now = datetime.now()
        names = dict(self.env['product.product'].browse(product_ids).name_get())
        for name in names:
            names[name] = names[name].encode('utf8')
        products = {}
        prods = self.env['product.product'].browse(product_ids)
        avail_qty = {}
        for prod in prods:
            products[prod.id] = [(now, prod.with_context(location=location_id,compute_child='child_of').qty_available,False,"START")]
            # products[prod.id] = [(now, prod.qty_available,False)]
            avail_qty[prod.id] = prod.qty_available

        if not loc_ids or not product_ids:
            return False

        self.env.cr.execute("select sum(r.product_qty * u.factor), r.date_expected, r.product_id,r.picking_id,r.origin "
                   "from stock_move r left join product_uom u on (r.product_uom=u.id) "
                   "where state IN %s"
                   "and location_id IN %s"
                   "and product_id = %s"
                   "group by date_expected,product_id,picking_id,origin "
                   "order by date_expected ASC",(('confirmed','assigned','waiting'),tuple(loc_ids) , product_ids,))
        for (qty, dt, prod_id,picking_id,origin) in self.env.cr.fetchall():
            products.setdefault(prod_id, [])
            products[prod_id].append((dt,-qty,picking_id,origin))

        self.env.cr.execute("select sum(r.product_qty * u.factor), r.date_expected, r.product_id, r.picking_id,r.origin "
                   "from stock_move r left join product_uom u on (r.product_uom=u.id) "
                   "where state IN %s"
                   "and location_dest_id IN %s"
                   "and product_id = %s"
                   "group by date_expected,product_id,picking_id,origin "
                   "order by date_expected ASC",(('confirmed','assigned','waiting'),tuple(loc_ids) ,product_ids,))
        for (qty, dt, prod_id,picking_id,origin) in self.env.cr.fetchall():
            products.setdefault(prod_id, [])
            products[prod_id].append((dt,qty,picking_id,origin))


        for prod in products:
            self.env['product.forecast'].search([("name","=",prod)]).unlink()
            for date,qty,picking_id,origin in products[prod]:
            # import ipdb; ipdb.set_trace()
                overdue = False
                if date.strptime('%Y-%m-%d') < now:
                    date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
                    overdue = True
                # else:
                #     date = date.strftime('%Y-%m-%d')

                self.env['product.forecast'].create({
                    "name":prod,
                    "qty":qty,
                    "picking_id":picking_id,
                    "date":date,
                    "overdue": overdue,
                    "origin":origin,
                    })
            all_forecasts = self.env['product.forecast'].search([('name','=',prod)],order='date ASC')
            previous_qty = 0
            self.stock_insufficient = False
            for item in all_forecasts:
                item.total_qty = previous_qty+item.qty
                previous_qty = item.total_qty
                #done here rather than in computed fieal finally
                if treshold > previous_qty:
                    self.stock_insufficient = True       