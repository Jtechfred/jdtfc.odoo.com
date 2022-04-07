odoo.define('jdtfc_pos.PaymentScreen', function(require) {

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosFrPaymentScreen = PaymentScreen => class extends PaymentScreen {
        async _postPushOrderResolve(order, order_server_ids) {
            try {
                if (this.env.pos.is_order_sequence()) {
                    const result = await this.rpc({
                        model: 'pos.order',
                        method: 'search_read',
                        domain: [['id', 'in', order_server_ids]],
                        fields: ['receipt_sequence'],
                        context: this.env.pos.session.user_context,
                    });
                    order.set_receipt_sequence(result[0].receipt_sequence || "");
                }
            } finally {
                return super._postPushOrderResolve(...arguments);
            }
        }
    };

    Registries.Component.extend(PaymentScreen, PosFrPaymentScreen);

    return PaymentScreen;
});
