$(document).ready(function() {

    var payment = $("div.enrollment-payment-method");
    var form = payment.find("form.payment");
    var payment_button_card = form.find("button.payment.card");
    var payment_button_invoice = form.find("button.payment.invoice");
    var invoice_info = form.find("div.invoice-info");
    var ajaxloader = form.find("img.ajaxloader");

    form.find("input[name='payment_method'][value='card']").change(function() {
        if($(this).is(":checked")) {
            payment_button_card.show();
            payment_button_invoice.hide();
            invoice_info.hide();
        }
    });
    form.find("input[name='payment_method'][value='invoice']").change(function() {
        if($(this).is(":checked")) {
            payment_button_card.hide();
            payment_button_invoice.show();
            invoice_info.show();
        }
    });

    form.submit(function() {
        payment_button.prop('disabled', true);
        ajaxloader.show();
    });

});
