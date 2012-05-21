$(document).ready(function() {

    $("form#household div.household").hide();
    $("form#household input[name='household']").click(function() {
        if($(this).prop('checked')) {
            $("form#household div.household").show();
        } else {
            $("form#household div.household").hide();
        }
    });

    $("form#household img.ajaxloader").hide();
    $("form#household input[name='zipcode']").keyup(function() {
        if($(this).val().match(/^\d{4}$/)) {
            $("form#household img.ajaxloader").show();
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#household input[name='location']").val(result);
            }).fail(function(result) {
                $("form#household input[name='location']").val("Ukjent postnummer");
                $("form#household div.control-group.zipcode").addClass('error');
            }).always(function(result) {
                $("form#household img.ajaxloader").hide();
            });
        } else {
            $("form#household input[name='location']").val("");
        }
    });
    $("form#household input[name='zipcode']").keyup();

    $("form#household input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning');
    });

    $("form#household input[name='address']").focusout(function() {
        if($(this).val() == "") {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#household input[name='zipcode']").focusout(function() {
        if(!$(this).val().match(/\d{4}/)) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#household").submit(function(e) {
        if($(this).find("input[name='address']").val() == '') {
            if(!confirm("Har du virkelig ingen adresse?\n\nDet finnes enkelte husstander i Norge som kun har postnummer og -sted, uten gateadresse. Hvis du bor på en av disse kan du gå videre, hvis ikke, trykk avbryt og fyll inn adressen.")) {
                e.preventDefault();
            }
        }
    });

});
