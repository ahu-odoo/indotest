# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(selection_add=[('x_fixed_cost', 'Fixed Cost Price')])