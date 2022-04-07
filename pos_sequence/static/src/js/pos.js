
odoo.define('jdtfc_pos.receipts', function (require) {
    "use strict";

var models = require('point_of_sale.models');

models.PosModel = models.PosModel.extend({
  // Method used to only bifurcate the method calls for PostPaymet action
  is_order_sequence: function(){
    return true;
  },
});

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({
    initialize: function() {
        _super_order.initialize.apply(this,arguments);
        this.receipt_sequence = this.receipt_sequence || false;
        this.save_to_db();
    },
    export_for_printing: function() {
      var result = _super_order.export_for_printing.apply(this,arguments);
      result.receipt_sequence = this.get_receipt_sequence();
      return result;
    },
    set_receipt_sequence: function (receipt_sequence){
      this.receipt_sequence = receipt_sequence;
    },
    get_receipt_sequence: function() {
      return this.receipt_sequence;
    },
    wait_for_push_order: function() {
      var result = _super_order.wait_for_push_order.apply(this,arguments);
      result = Boolean(result || this.pos.is_order_sequence());
      return result;
    }
});

});
