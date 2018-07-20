from odoo import api, fields, models, _

class account_invoice(models.Model):
    _inherit = "account.invoice"

    user_id = fields.Many2one(track_visibility=False)            

class sector(models.Model):
    _name = 'sale.sector'

    name = fields.Char('Sector')   

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    sector_id = fields.Many2one('sale.sector', 'Sector')   

class sale_order(models.Model):
    _inherit = "sale.order"

    compute_from_project_qty = fields.Boolean('Compute from project QTY')
    project_qty = fields.Float('Project QTY', default=0.0)
    sector_id = fields.Many2one('sale.sector', 'Sector') 
    potential_duplicate = fields.Boolean('Potential duplicate', readonly=True, compute='_compute_duplicate', store=True, help='Based on the customer reference, we think this SO is potentially a duplicate SO')

    @api.model
    def create(self, vals):
        so = super(sale_order, self).create(vals)
        group = self.env.ref('indo_sale.auto_add_so')
        so.message_subscribe_users(user_ids=group.users.ids)
        return  so

    @api.onchange('compute_from_project_qty')
    def onchange_compute_from_project_qty(self):
        if not self.compute_from_project_qty:
            project_qty=0

    @api.one
    @api.depends('partner_id', 'client_order_ref')
    def _compute_duplicate(self):
        potential_id = self.search([('partner_id','=',self.partner_id.id), ('client_order_ref','=',self.client_order_ref)])
        self.potential_duplicate = True if len(potential_id)>=2 else False

class product(models.Model):
    _inherit = "product.template"

    state = fields.Selection([  ('draft', 'In Development'),
                                ('sellable', 'Normal'),
                                ('end', 'End of Lifecycle'),
                                ('obsolete', 'Obsolete')], "Status")




class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    product_status = fields.Selection(related='product_id.state',string='Product State')


class purchase_order(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        # TODO ? maybe add a subtype_ids to message_subscribe_users even though there's a default value?
        po = super(purchase_order, self).create(vals)
        group = self.env.ref('indo_sale.auto_add_po')
        po.message_subscribe_users(user_ids=group.users.ids)
        return  po
