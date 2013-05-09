$(document).ready(function() {

    var form = $("form.account-info");

    Validator.validate({
        method: 'full_name',
        control_group: form.find("div.control-group.name"),
        input: form.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: form.find("div.control-group.email"),
        input: form.find("input[name='email']"),
        req: true
    });

    var control_group = form.find("div.control-group.sherpa-email");
    if(control_group.length > 0) {
        Validator.validate({
            method: 'email',
            control_group: control_group,
            input: control_group.find("input[name='sherpa-email']"),
            req: false
        });
    }

    Validator.validate({
        method: 'phone',
        control_group: form.find("div.control-group.phone_home"),
        input: form.find("input[name='phone_home']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        control_group: form.find("div.control-group.phone_mobile"),
        input: form.find("input[name='phone_mobile']"),
        req: false
    });

    Validator.validate({
        method: 'address',
        control_group: form.find("div.control-group.address"),
        input: form.find("input[name='address']"),
        req: true
    });

    Validator.validateZipcode(
        form.find("div.control-group.zipcode"),
        form.find("input[name='zipcode']"),
        form.find("input[name='area']"),
        form.find("img.ajaxloader.zipcode")
    );

    // Trigger all validations
    Validator.trigger();
    Validator.triggerZipcode(form.find("input[name='zipcode']"));

    form.find("input[name='toggle-sherpa-email']").change(function() {
        if($(this).is(':checked')) {
            form.find("input[name='sherpa-email']").removeAttr('readonly');
        } else {
            form.find("input[name='sherpa-email']").val('').attr('readonly', true).focusout();
        }
    });

});
