$(document).ready(function() {

    var form = $("form#payment");
    var payment_button = form.find("button.payment");
    var invoice_info = form.find("div.invoice-info");
    var ajaxloader = form.find("img.ajaxloader");

    form.find("input[name='payment_method'][value='card']").change(function() {
        if($(this).is(":checked")) {
            payment_button.html('Til betaling <i class="icon-arrow-right"></i>');
            invoice_info.hide();
        }
    });
    form.find("input[name='payment_method'][value='invoice']").change(function() {
        if($(this).is(":checked")) {
            payment_button.html('Send bestilling <i class="icon-ok"></i>');
            invoice_info.show();
        }
    });

    form.submit(function() {
        payment_button.prop('disabled', true);
        ajaxloader.show();
        // The adform guys advised us to defer this call even though it probably shouldn't be
        setTimeout(function() {
            if(typeof adf !== 'undefined') {
                adf.track(133425,2765716,{});
            }
        }, 0);
    });

});
