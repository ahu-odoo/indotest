{
    'name': 'Indo Web',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
OpenERP Web INDO module.
========================

This module provides the core of the Odoo INDO Web Client.
        """,
    'depends': ['web','base'],
    'auto_install': True,
    'data': [
        'views/assets_indo.xml'
    ],
    'qweb' : [
    ],
}
