$(document).ready(function() {

    $("form#household img.ajaxloader").hide();
    $("form#household select[name='country']").chosen();

    // Zipcode-validations
    var zipcode_control_group = $("form#household div.control-group.zipcode");
    var zipcode = $("form#household input[name='zipcode']");
    var area = $("form#household input[name='area']");
    var loader = $("form#household img.zip.ajaxloader");

    $("form#household select[name='country']").change(function() {
        setAddressState(false);
    });
    setAddressState(true);
    function setAddressState(first) {
        var sel = $("form#household select[name='country'] option:selected");
        if(sel.val() == 'NO') {
            $("form#household div.world").hide();
            $("form#household div.scandinavia").show();
            $("form#household div.yearbook").hide();
            area.attr('disabled', true);
            Validator.validateZipcode(zipcode_control_group, zipcode, area, loader);
            if(!first || (first && zipcode.val() != '')) {
                Validator.triggerZipcode(zipcode);
            }
        } else if(sel.parents("optgroup#scandinavia").length > 0) {
            $("form#household div.world").hide();
            $("form#household div.scandinavia").show();
            $("form#household div.yearbook").show();
            area.removeAttr('disabled');
            Validator.stopZipcodeValidation(zipcode);
            zipcode.focusout();
        } else {
            $("form#household div.world").show();
            $("form#household div.scandinavia").hide();
            $("form#household div.yearbook").show();
        }
    }

    $("form#household input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    $("form#household input[name='address1']").focusout(function() {
        if($(this).val() == "") {
            $(this).parents("div.control-group").addClass('error');
        } else {
            $(this).parents("div.control-group").addClass('success');
        }
    });

    $("form#household input[name='address2'], form#household input[name='address3']").focusout(function() {
        $(this).parents("div.control-group").addClass('success');
    });

    zipcode.focusout(function() {
        if($("form#household select[name='country'] option:selected").val() != 'NO') {
            if($(this).val() == '' || area.val() == '') {
                zipcode_control_group.removeClass('success').addClass('error');
            } else {
                zipcode_control_group.removeClass('error').addClass('success');
            }
        }
    });

    area.focusout(function() {
        if($(this).val() == '' || zipcode.val() == '') {
            zipcode_control_group.removeClass('success').addClass('error');
        } else {
            zipcode_control_group.removeClass('error').addClass('success');
        }
    });

    $("form#household").submit(function(e) {
        if($(this).find("input[name='address1']").val() == '' &&
           $("form#household select[name='country'] option:selected").val() == 'NO' &&
           !confirm("Har du glemt å fylle ut gateadressen?\n\nHvis du ikke har gateadresse, klikker du bare OK for å gå videre.")) {
                e.preventDefault();
        }
    });

    /* Existing */
    $("form#household button.search").click(function(e) {
        e.preventDefault();
        $("div.existing-result").show();
        var button = $(this);
        button.attr('disabled', true);
        $("form#household img.existing.ajaxloader").show();
        var data = {
            id: $("form#household input[name='existing']").val(),
            zipcode: $("form#household input[name='zipcode']").val(),
            country: $("form#household select[name='country'] option:selected").val()
        }
        $("div.existing-result span.result").hide();
        $("div.existing-result span.result").removeClass('success error');
        $.ajaxQueue({
            url: '/innmelding/eksisterende/',
            data: { data: JSON.stringify(data) }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'bad_zipcode') {
                $("div.existing-result span.result").text("Du må oppgi riktig postnummer før du søker.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'invalid_id') {
                $("div.existing-result span.result").text("Ugyldig medlemsnummer oppgitt.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actor.does_not_exist') {
                $("div.existing-result span.result").text("Fant ingen medlemmer med dette medlemsnummeret.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actor.too_young') {
                $("div.existing-result span.result").text("Det angitte medlemmet er bare " + result.age + " år ved utgangen av året, og kan ikke være hovedmedlem.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.error == 'actoraddress.does_not_exist') {
                $("div.existing-result span.result").text("Det angitte medlemmet bor ikke på samme adresse som dere.");
                $("div.existing-result span.description").hide();
                $("div.existing-result span.result").addClass('error');
            } else if(result.name != '') {
                $("div.existing-result span.result").text(result.name + ', ' + result.address);
                $("div.existing-result span.description").show();
                $("div.existing-result span.result").addClass('success');
            }
        }).fail(function(result) {
            // Todo
        }).always(function() {
            button.removeAttr('disabled');
            $("form#household img.existing.ajaxloader").hide();
            $("div.existing-result span.result").show();
        });
    });

    if(existing) {
        $("form#household button.search").click();
    } else {
        $("div.existing-result").hide();
    }

    if(window.trigger_form_validations) {
        $("form#household input").focusout();
        Validator.triggerZipcode(zipcode);
    }
});
