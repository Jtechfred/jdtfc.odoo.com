# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ShareCommerceController(http.Controller):
    _return_url = '/payment/share_commerce/return'
   

    @http.route('/payment/share_commerce/return', type='http', auth='public', methods=['GET'], csrf=False)
    def share_commerce_return(self, **data):
        """ Share Commerce."""
        _logger.info('Share Commercce: entering form_feedback with data data %s', pprint.pformat(data))  # debug
        request.env['payment.transaction'].sudo().form_feedback(data, 'share_commerce')
        return werkzeug.utils.redirect('/payment/process')

