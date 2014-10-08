$(function() {

    Validator.validate({
        method: 'email',
        form_group: $('[data-dnt-form-group="email"]'),
        input: $('input[name="email"]'),
        req: true
    });

    var form_group = $('[data-dnt-form-group="sherpa-email"]');
    if(form_group.length > 0) {
        Validator.validate({
            method: 'email',
            form_group: form_group,
            input: form_group.find('input[name="sherpa-email"]'),
            req: false
        });
    }

    Validator.validatePasswords({
        form_group: $('[data-dnt-form-group="password"], [data-dnt-form-group="password-repeat"]'),
        pass1: $('input[name="password"]'),
        pass2: $('input[name="password-repeat"]'),
        min_length: Turistforeningen.user_password_length,
        hints: $('div.password-hints *')
    });

    $('input[name="toggle-sherpa-email"]').change(function() {
        if($(this).is(':checked')) {
            $('input[name="sherpa-email"]').prop('readonly', false);
        } else {
            $('input[name="sherpa-email"]').val('').prop('readonly', true).focusout();
        }
    });

});
