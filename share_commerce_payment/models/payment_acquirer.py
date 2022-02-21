# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import hashlib
from hashlib import sha256
import logging
import hmac

import logging

from werkzeug import urls
from collections import OrderedDict

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



    # -------------------------------------------------------------------------------------------
    #       Base Method
    #  check in payment module for refernce, removing the share_commerce from the method name 
    # -------------------------------------------------------------------------------------------


    def share_commerce_form_generate_values(self, values):
    
        # Make ordered dict to avoid jumbling
        rendering_values = OrderedDict()
        return_url = urls.url_join(self.get_base_url(), ShareCommerceController._return_url)

        rendering_values['MerchantID'] = self.scp_merchantid
        rendering_values['CurrencyCode'] = 'MYR' #IMP ME LATER,
        rendering_values['TxnAmount'] = values.get('amount')
        rendering_values['MerchantOrderNo'] =   values.get('reference')
        rendering_values['MerchantOrderDesc']= values.get('reference')
        rendering_values['MerchantRef1'] = 'mref1'
        rendering_values['MerchantRef2'] = 'mref2'
        rendering_values['MerchantRef3'] = 'mref3'
        rendering_values['CustReference'] =  values.get('partner_name', '') #IMP ME LATER
        rendering_values['CustName'] = values.get('partner_name', '')
        rendering_values['CustEmail'] =  values.get('partner_email', '')
        rendering_values['CustPhoneNo'] =  values.get('partner_phone', '')
        rendering_values['CustAddress1'] =  values.get('partner_address','')
        rendering_values['CustAddress2'] =  values.get('partner_zip','')
        rendering_values['CustCountryCode'] = 'MY' #values.get('partner_country').code if values.get('partner_country') else ''
        rendering_values['CustAddressState'] =   values.get('partner_state').code if values.get('partner_state') else ''
        rendering_values['CustAddressCity'] =  values.get('partner_city', '')
        rendering_values['RedirectUrl'] = return_url
        
        # get the sha256 string sign with rendering dic current values
        scp_sign = self._share_commerce_generate_digital_sign(rendering_values)
        rendering_values['api_url']= self.share_commerce_get_form_action_url() # I guess we can remove in v14 check later on
        rendering_values['SCSign']= scp_sign
        
        return rendering_values


    def share_commerce_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        print()
        return self._get_share_commerce_urls(environment)
