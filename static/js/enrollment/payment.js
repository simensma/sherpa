$(document).ready(function() {

    $("form#payment input[name='payment-method'][value='card']").change(function() {
        if($(this).is(":checked")) {
            $("a.payment").html('Til betaling <i class="icon-arrow-right"></i>');
            $("div.invoice-info").hide();
        }
    });
    $("form#payment input[name='payment-method'][value='invoice']").change(function() {
        if($(this).is(":checked")) {
            $("a.payment").html('Send bestilling <i class="icon-ok"></i>');
            $("div.invoice-info").show();
        }
    });

});
