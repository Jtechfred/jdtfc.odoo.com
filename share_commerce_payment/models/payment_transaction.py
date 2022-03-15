# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from werkzeug import urls
from odoo.addons.share_commerce_payment.controllers.main import ShareCommerceController


_logger = logging.getLogger(__name__)


RESPONSE_CODE = {
    "Application Error" : "IE",
    "Success": "00",
    "Pending": "09",
    "Failed": "99"
}

"""Below dict for refund for later on purpose"""

# REFUND_CODE = {
#     "FR" : "Fraudulent",
#     "DP" : "Duplicate",
#     "RC" : "Request by customer",
#     "OT" : "Other",
# }


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # ------------------------------------------------------------
    #       Base methods 
    #   check in payment module for refernce, removing the share_commerce from the method name 
    # -------------------------------------------------------------


    def _get_specific_rendering_values(self, processing_values):
        # Make ordered dict to avoid jumbling
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'share_commerce':
            return res
        rendering_values = {}
        return_url = urls.url_join(self.get_base_url(), ShareCommerceController._return_url)

        rendering_values['MerchantID'] = self.acquirer_id.scp_merchantid
        rendering_values['CurrencyCode'] = self.currency_id.name
        rendering_values['TxnAmount'] = processing_values.get('amount')
        rendering_values['MerchantOrderNo'] =   processing_values.get('reference')
        rendering_values['MerchantOrderDesc']= processing_values.get('reference')
        rendering_values['CustName'] = self.partner_name
        rendering_values['CustEmail'] = self.partner_email
        rendering_values['CustPhoneNo'] =  self.partner_phone
        rendering_values['CustAddress1'] =  self.partner_address
        rendering_values['CustAddress2'] =  self.partner_zip
        rendering_values['CustCountryCode'] = self.partner_country_id.code
        rendering_values['CustAddressState'] = self.partner_state_id.name
        rendering_values['CustAddressCity'] =  self.partner_city
        rendering_values['RedirectUrl'] = return_url

        # get the sha256 string sign with rendering dic current values
        scp_sign = self.acquirer_id._share_commerce_generate_digital_sign(rendering_values)
        rendering_values['api_url']= self.acquirer_id.share_commerce_get_form_action_url() # I guess we can remove in v14 check later on
        rendering_values['SCSign']= scp_sign

        return rendering_values

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Given a data dict coming from Share Commerce, verify it and find the related
        transaction record. """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'share_commerce':
            return tx
        reference = data.get('MerchantOrderNo')
        shasign = data.get('SCSign')
        if not reference or not shasign:
            raise ValidationError(
                "Share Commerce: " + _(
                    "Received data with missing reference (%(ref)s) or shasign (%(sign)s)",
                    ref=reference, sign=shasign
                )
            )

        tx = self.search([('reference', '=', reference), ('provider', '=', 'share_commerce')])
        if not tx:
            raise ValidationError(
                "Share Commerce: " + _("No transaction found matching reference %s.", reference)
            )

        # Verify signature
        data['SCSign'] =''
        shasign_check = tx.acquirer_id._share_commerce_generate_digital_sign(data)
        if shasign_check != shasign:
            raise ValidationError(
                "Share Commerce: " + _(
                    "Invalid shasign: received %(sign)s, computed %(check)s",
                    sign=shasign, check=shasign_check
                )
            )

        return tx


    def _process_feedback_data(self, data):
        super()._process_feedback_data(data)
        if self.provider != 'share_commerce':
            return

        status_code = str(data.get('RespCode') or 0)
        self.acquirer_reference = data.get('TxnRefNo', False)

        if status_code in RESPONSE_CODE['Pending']:
            self._set_pending()
            return True
        elif status_code in RESPONSE_CODE['Success']:
            self._set_done()
            return True
        elif status_code in RESPONSE_CODE['Failed']:
            self._set_canceled()
            return False
        elif status_code in RESPONSE_CODE['Application Error']:
            self._set_error((_("An Application Error occurred during processing of your payment (code %s). Please try again.", status_code)))
            return False
        else:
            _logger.error("Share Commerce: received unknown status code: %s", status_code)
            self._set_error("Share Commerce: " + _("Unknown status code: %s", status_code))
            return False
