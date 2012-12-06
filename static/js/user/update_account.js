$(document).ready(function() {

    Validator.validate({
        method: 'full_name',
        control_group: $("div.control-group.name"),
        input: $("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

    Validator.validate({
        method: 'phone',
        control_group: $("div.control-group.phone_home"),
        input: $("input[name='phone_home']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        control_group: $("div.control-group.phone_mobile"),
        input: $("input[name='phone_mobile']"),
        req: false
    });

    $("input[name='dob']").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        startView: 'decade',
        autoclose: true,
        language: 'nb'
    }).on('hide', function() {
        Validator.performValidation({
            method: 'date',
            control_group: $("div.control-group.dob"),
            input: $("input[name='dob']"),
            req: true
        });
    });

    Validator.validate({
        method: 'address',
        control_group: $("div.control-group.address"),
        input: $("input[name='address']"),
        req: true
    });

    Validator.validateZipcode(
        $("div.control-group.zipcode"),
        $("input[name='zipcode']"),
        $("input[name='area']"),
        $("img.ajaxloader.zipcode")
    );

    Validator.validatePasswords({
        control_group: $("div.control-group.password, div.control-group.password-repeat"),
        pass1: $("input[name='password']"),
        pass2: $("input[name='password-repeat']"),
        min_length: user_password_length,
        hints: $("div.form-hints div.password-hint")
    });

    // Trigger all validations
    Validator.trigger();
    $("input[name='dob']").datepicker('hide');
    Validator.triggerZipcode($("input[name='zipcode']"));

});
