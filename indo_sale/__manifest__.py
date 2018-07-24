# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Indo Sale Improvements',
    'version': '1.1',
    'author': 'Odoo SA',
    'website': '',
    'category': 'Stock',
    'sequence': 18,
    'summary': 'Allows so automatically add/removes followers',
    'depends': ['stock_account','sale_stock','crm','purchase'],
    'description': """ Adding new features to sale module
    - Allows so automatically add/removes followers
    - Adds the notion of sectors and then rules linked to it
    - Shows a message on SO for potential duplicated SOs
    """,
    'data': [
         'views/sale.xml',
         'views/res_users.xml',
         'security/indo_sale.xml',
         'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


#changes to bring in migration scripts
# view named sale.order.list.select.lawrence needs to inherit from  OR sale.order.remove.filter.lawrence needs to be deactivated