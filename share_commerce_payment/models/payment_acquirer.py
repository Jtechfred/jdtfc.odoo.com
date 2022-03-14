# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import hashlib
from hashlib import sha256
import logging
import hmac

import logging

from werkzeug import urls

from odoo.addons.share_commerce_payment.controllers.main import ShareCommerceController

from odoo import fields, models

_logger = logging.getLogger(__name__)



class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    # ---------------------------------------------------------------------------
    # Fields Declaration
    # ---------------------------------------------------------------------------
    # below variables, obj,func namings contains 'scp' which is stands for share commerce payment.
    # ---------------------------------------------------------------------------

    scp_merchantid = fields.Char(
        string="Merchant ID", 
        help="Merchant ID of Share Commerce which was provided by Share Commerce in onboard email.",
        required_if_provider='share_commerce',
        groups='base.group_system'
    )

    scp_secret_key = fields.Char(
        string="Secret Key", required_if_provider='share_commerce',
        help="Secret Key of Share Commerce which was provided by Share Commerce in onboard email.", 
        groups='base.group_system')

    scp_production_url = fields.Char('Production URL' )
    scp_staging_url = fields.Char('Staging URL')

    provider = fields.Selection(
        selection_add=[('share_commerce', "Share Commerce")], 
        ondelete={'share_commerce': 'set default'}
    )


    # ------------------------------------------------------------
    #       Custom Business Methods 
    # -------------------------------------------------------------

    def _scp_url_formatter(self, url):
        """ Return the Formatted URL 

        :return: The Formatted URL
        :rtype: str
        """
        if not url: return False     
        url.strip()
        if url[-1] != '/':
            url +'/'
        return url

    def _share_commerce_generate_digital_sign(self,values):
        """ Return the SHA256 string.

        Note: Our Ultimate goal is to add only the values() of dict without a single space
              which we used to generate the sign str with sha256

        :return: The hex-dec equivalant String 
        :rtype: str
        """
       
        if not values: return False
        self.ensure_one()
        key = self.scp_secret_key
        data = ''.join([str(vals) for vals in values.values()])
 
        has =hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()
        return has

    def _get_share_commerce_urls(self, environment):
        """ Share Commerce URLs
        """
        if environment == 'prod':
            return self._scp_url_formatter(self.scp_production_url)
        else:
            return self._scp_url_formatter(self.scp_staging_url)

    def share_commerce_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_share_commerce_urls(environment)

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'share_commerce':
            return super()._get_default_payment_method_id()
        return self.env.ref('share_commerce_payment.payment_method_share_commerce').id
