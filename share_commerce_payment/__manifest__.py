# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Share commerce Payment",
    'summary': """ Payment Acquirer: Share Commerce Payment""",
    'description': """ 
        Task ID:2733364
        Payment Acquirer: Share Commerce Payment
        
    """,
    'category': 'Accounting/Payment Acquirers',
    'author': 'Odoo PS - India',
    'version': '15.0.1.0.1',
   
    'depends': [
        'payment',
    ],

    'data': [
        'views/payment_share_commerce_templates.xml',
        'views/payment_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'application': True,
    # 'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
    'license': 'OEEL-1',

}
