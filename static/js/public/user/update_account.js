$(function() {

    var form = $("form.account-info");

    Validator.validate({
        method: 'email',
        form_group: form.find('[data-dnt-form-group="email"]'),
        input: form.find("input[name='email']"),
        req: true
    });

    var sherpa_email = form.find('[data-dnt-form-group="sherpa-email"]');
    if(sherpa_email.length > 0) {
        Validator.validate({
            method: 'email',
            form_group: sherpa_email,
            input: sherpa_email.find("input[name='sherpa-email']"),
            req: false
        });
    }

    Validator.validate({
        method: 'phone',
        form_group: form.find('[data-dnt-form-group="phone_home"]'),
        input: form.find("input[name='phone_home']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        form_group: form.find('[data-dnt-form-group="phone_mobile"]'),
        input: form.find("input[name='phone_mobile']"),
        req: false
    });

    var address = form.find('[data-dnt-form-group="address"]');
    Validator.validate({
        method: 'address',
        form_group: address,
        input: address.find("input[name='address']"),
        req: true,
        opts: { max_length: Turistforeningen.address_field_max_length }
    });

    var address2 = form.find('[data-dnt-form-group="address2"]');
    Validator.validate({
        method: 'address',
        form_group: address2,
        input: address2.find("input[name='address2']"),
        req: true,
        opts: { max_length: Turistforeningen.address_field_max_length }
    });

    var address3 = form.find('[data-dnt-form-group="address3"]');
    Validator.validate({
        method: 'address',
        form_group: address3,
        input: address3.find("input[name='address3']"),
        req: true,
        opts: { max_length: Turistforeningen.address_field_max_length }
    });

    Validator.validateZipcode(
        form.find('[data-dnt-form-group="zipcode"]'),
        form.find("input[name='zipcode']"),
        form.find("input[name='area']"),
        form.find("img.ajaxloader.zipcode")
    );

    // Trigger all validations
    Validator.trigger();
    Validator.triggerZipcode(form.find("input[name='zipcode']"));

    form.find("input[name='toggle-sherpa-email']").change(function() {
        if($(this).is(':checked')) {
            form.find("input[name='sherpa-email']").prop('readonly', false);
        } else {
            form.find("input[name='sherpa-email']").val('').prop('readonly', true).focusout();
        }
    });

});
