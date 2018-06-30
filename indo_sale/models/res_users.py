import itertools
import math
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class res_users(models.Model):
    _inherit = "res.users"

    sector_ids = fields.Many2many('sale.sector', 'sector_user_rel', 'user_id', 'sector_id',string="Sectors")