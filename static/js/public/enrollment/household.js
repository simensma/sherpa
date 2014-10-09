$(function() {

    var form = $('[data-dnt-container="household-form"]');
    var existing_input = form.find('input[name="existing"]');
    var existing_trigger = form.find('[data-dnt-trigger="existing"]');
    var existing_result = form.find("div.existing-result");

    form.find("select[name='country']").chosen();

    // Zipcode-validations
    var zipcode_form_group = form.find('[data-dnt-form-group="zipcode"]');
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
            form.find('[data-dnt-form-group="yearbook"]').hide();
            area.prop('disabled', true);
            Validator.validateZipcode(zipcode_form_group, zipcode, area, loader);
            if(!first || (first && zipcode.val() !== '')) {
                Validator.triggerZipcode(zipcode);
            }
        } else if(sel.parents("optgroup#scandinavia").length > 0) {
            form.find("div.world").hide();
            form.find("div.scandinavia").show();
            form.find('[data-dnt-form-group="yearbook"]').show();
            area.prop('disabled', false);
            Validator.stopZipcodeValidation(zipcode);
            zipcode.focusout();
        } else {
            form.find("div.world").show();
            form.find("div.scandinavia").hide();
            form.find('[data-dnt-form-group="yearbook"]').show();
        }
    }

    form.find("input").focus(function() {
        $(this).parents('[data-dnt-form-group]').removeClass('has-error has-warning has-success');
    });

    form.find("input[name='address1']").focusout(function() {
        if($(this).val() === "") {
            $(this).parents('[data-dnt-form-group]').addClass('has-error');
        } else {
            $(this).parents('[data-dnt-form-group]').addClass('has-success');
        }
    });

    form.find("input[name='address2'], input[name='address3']").focusout(function() {
        $(this).parents('[data-dnt-form-group]').addClass('has-success');
    });

    zipcode.focusout(function() {
        if(form.find("select[name='country'] option:selected").val() != 'NO') {
            if($(this).val() === '' || area.val() === '') {
                zipcode_form_group.removeClass('has-success').addClass('has-error');
            } else {
                zipcode_form_group.removeClass('has-error').addClass('has-success');
            }
        }
    });

    area.focusout(function() {
        if($(this).val() === '' || zipcode.val() === '') {
            zipcode_form_group.removeClass('has-success').addClass('has-error');
        } else {
            zipcode_form_group.removeClass('has-error').addClass('has-success');
        }
    });

    form.submit(function(e) {
        if($(this).find("input[name='address1']").val() === '' &&
           form.find("select[name='country'] option:selected").val() == 'NO' &&
           !confirm($(this).attr("data-confirm-no-address"))) {
                e.preventDefault();
        }
    });

    /* Existing */

    existing_input.keydown(function(e) {
        if(e.which === 13) { // Enter
            e.preventDefault();
            existing_trigger.click();
        }
    });

    existing_trigger.click(function(e) {
        e.preventDefault();
        existing_result.show();
        var button = $(this);
        button.prop('disabled', true);
        form.find("img.existing.ajaxloader").show();
        var data = {
            id: existing_input.val(),
            zipcode: form.find("input[name='zipcode']").val(),
            country: form.find("select[name='country'] option:selected").val()
        };
        existing_result.find("span.jq-hide").hide();
        $.ajaxQueue({
            url: form.attr('data-existing-url'),
            data: { data: JSON.stringify(data) }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'bad_zipcode') {
                existing_result.find("span.bad-zipcode").show();
            } else if(result.error == 'invalid_id') {
                existing_result.find("span.invalid-id").show();
            } else if(result.error == 'actor.does_not_exist') {
                existing_result.find("span.actor-does-not-exist").show();
            } else if(result.error == 'actor.has_not_paid') {
                existing_result.find("span.actor-has-not-paid").show();
            } else if(result.error == 'actor.too_young') {
                var too_young = existing_result.find("span.too-young");
                too_young.show();
                too_young.find("span.age").text(result.age);
            } else if(result.error == 'actor.is_household_member') {
                existing_result.find("span.is-household-member").show();
            } else if(result.error == 'actoraddress.does_not_exist') {
                existing_result.find("span.actoraddress-does-not-exist").show();
            } else if(result.name !== '') {
                var success = existing_result.find("span.success");
                success.show();
                success.find("span.result").text(result.name + ', ' + result.address);
            }
        }).fail(function(result) {
            existing_result.find("span.technical-error").show();
        }).always(function() {
            button.prop('disabled', false);
            form.find("img.existing.ajaxloader").hide();
        });
    });

    if(Turistforeningen.existing) {
        existing_trigger.click();
    } else {
        existing_result.hide();
    }

    if(Turistforeningen.trigger_form_validations) {
        form.find("input").focusout();
        Validator.triggerZipcode(zipcode);
    }
});
