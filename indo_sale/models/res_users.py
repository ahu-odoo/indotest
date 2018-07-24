from odoo import api, fields, models, _

class res_users(models.Model):
    _inherit = "res.users"

    sector_ids = fields.Many2many('sale.sector', 'sector_user_rel', 'user_id', 'sector_id',string="Sectors")