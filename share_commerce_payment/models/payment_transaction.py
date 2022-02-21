# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging


from odoo import _, api, models, fields
from odoo.exceptions import ValidationError


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


    @api.model
    def _share_commerce_form_get_tx_from_data(self, data):
        """ Given a data dict coming from Share Commerce, verify it and find the related
        transaction record. """
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


    def _share_commerce_form_validate(self, data):
        status_code = str(data.get('RespCode') or 0)
        self.acquirer_reference = data.get('TxnRefNo', False)

        if status_code in RESPONSE_CODE['Pending']:
            self._set_transaction_pending()
            return True
        elif status_code in RESPONSE_CODE['Success']:
            self._set_transaction_done()
            return True
        elif status_code in RESPONSE_CODE['Failed']: #CHECK ME
            self._set_transaction_cancel()
            return False
            # self._set_transaction_error((_("Your payment was Failed (code %s). Please try again.", status_code)))
        elif status_code in RESPONSE_CODE['Application Error']:
            self._set_transaction_error((_("An Application Error occurred during processing of your payment (code %s). Please try again.", status_code)))
            return False
        else:
            _logger.error("Share Commerce: received unknown status code: %s", status_code)
            self._set_transaction_error("Share Commerce: " + _("Unknown status code: %s", status_code))
            return False
