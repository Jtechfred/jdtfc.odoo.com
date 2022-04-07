# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = "pos.order"

    receipt_sequence = fields.Char('Receipt Sequence')

    @api.model
    def create(self, values):
        res = super(PosOrder, self).create(values)
        config_seq = res.session_id.config_id.order_seq
        res.write({'receipt_sequence': "{:04d}".format(config_seq)})
        res.session_id.config_id.write({'order_seq': config_seq + 1})
        return res

class pos_config(models.Model):
    _inherit = 'pos.config'

    order_seq = fields.Integer('Next Order Sequence', default=1)

    @api.model
    def _reset_pos_order_sequence(self):
        self.search([]).write({'order_seq': 1})
