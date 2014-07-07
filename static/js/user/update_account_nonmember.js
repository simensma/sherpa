$(function() {

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

    var control_group = $("div.control-group.sherpa-email");
    if(control_group.length > 0) {
        Validator.validate({
            method: 'email',
            control_group: control_group,
            input: control_group.find("input[name='sherpa-email']"),
            req: false
        });
    }

    Validator.validatePasswords({
        control_group: $("div.control-group.password, div.control-group.password-repeat"),
        pass1: $("input[name='password']"),
        pass2: $("input[name='password-repeat']"),
        min_length: Turistforeningen.user_password_length,
        hints: $("div.password-hints *")
    });

    $("input[name='toggle-sherpa-email']").change(function() {
        if($(this).is(':checked')) {
            $("input[name='sherpa-email']").prop('readonly', false);
        } else {
            $("input[name='sherpa-email']").val('').prop('readonly', true).focusout();
        }
    });

});
