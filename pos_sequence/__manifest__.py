# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Sequence',
    'version': '14.0',
    'category': 'POS',
    'summary': 'Set everyday Running sequence number of pos orders',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_data.xml',
        'views/pos_views.xml',
        'views/pos_assets.xml',
    ],
    'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    'installable': True,
}
