$(document).ready(function() {

    var form = $("form#household");

    form.find("img.ajaxloader").hide();
    form.find("select[name='country']").chosen();

    // Zipcode-validations
    var zipcode_control_group = form.find("div.control-group.zipcode");
    var zipcode = form.find("input[name='zipcode']");
    var area = form.find("input[name='area']");
    var loader = form.find("img.zip.ajaxloader");

    form.find("select[name='country']").change(function() {
        setAddressState(false);
    });
    setAddressState(true);
    function setAddressState(first) {
        var sel = form.find("select[name='country'] option:selected");
        if(sel.val() == 'NO') {
            form.find("div.world").hide();
            form.find("div.scandinavia").show();
            form.find("div.yearbook").hide();
            area.prop('disabled', true);
            Validator.validateZipcode(zipcode_control_group, zipcode, area, loader);
            if(!first || (first && zipcode.val() !== '')) {
                Validator.triggerZipcode(zipcode);
            }
        } else if(sel.parents("optgroup#scandinavia").length > 0) {
            form.find("div.world").hide();
            form.find("div.scandinavia").show();
            form.find("div.yearbook").show();
            area.prop('disabled', false);
            Validator.stopZipcodeValidation(zipcode);
            zipcode.focusout();
        } else {
            form.find("div.world").show();
            form.find("div.scandinavia").hide();
            form.find("div.yearbook").show();
        }
    }

    form.find("input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    form.find("input[name='address1']").focusout(function() {
        if($(this).val() === "") {
            $(this).parents("div.control-group").addClass('error');
        } else {
            $(this).parents("div.control-group").addClass('success');
        }
    });

    form.find("input[name='address2'], input[name='address3']").focusout(function() {
        $(this).parents("div.control-group").addClass('success');
    });

    zipcode.focusout(function() {
        if(form.find("select[name='country'] option:selected").val() != 'NO') {
            if($(this).val() === '' || area.val() === '') {
                zipcode_control_group.removeClass('success').addClass('error');
            } else {
                zipcode_control_group.removeClass('error').addClass('success');
            }
        }
    });

    area.focusout(function() {
        if($(this).val() === '' || zipcode.val() === '') {
            zipcode_control_group.removeClass('success').addClass('error');
        } else {
            zipcode_control_group.removeClass('error').addClass('success');
        }
    });

    form.submit(function(e) {
        if($(this).find("input[name='address1']").val() === '' &&
           form.find("select[name='country'] option:selected").val() == 'NO' &&
           !confirm("Har du glemt å fylle ut gateadressen?\n\nHvis du ikke har gateadresse, klikker du bare OK for å gå videre.")) {
                e.preventDefault();
        }
    });

    /* Existing */
    form.find("button.search").click(function(e) {
        e.preventDefault();
        $("div.existing-result").show();
        var button = $(this);
        button.prop('disabled', true);
        form.find("img.existing.ajaxloader").show();
        var data = {
            id: form.find("input[name='existing']").val(),
            zipcode: form.find("input[name='zipcode']").val(),
            country: form.find("select[name='country'] option:selected").val()
        };
        $("div.existing-result span.result").hide();
        $("div.existing-result span.result").removeClass('success error');
        $.ajaxQueue({
            url: form.attr('data-existing-url'),
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
            } else if(result.name !== '') {
                $("div.existing-result span.result").text(result.name + ', ' + result.address);
                $("div.existing-result span.description").show();
                $("div.existing-result span.result").addClass('success');
            }
        }).fail(function(result) {
            // Todo
        }).always(function() {
            button.prop('disabled', false);
            form.find("img.existing.ajaxloader").hide();
            $("div.existing-result span.result").show();
        });
    });

    if(Turistforeningen.existing) {
        form.find("button.search").click();
    } else {
        $("div.existing-result").hide();
    }

    if(Turistforeningen.trigger_form_validations) {
        form.find("input").focusout();
        Validator.triggerZipcode(zipcode);
    }
});
