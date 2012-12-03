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

    Validator.validatePasswords({
        control_group: $("div.control-group.password, div.control-group.password-repeat"),
        pass1: $("input[name='password']"),
        pass2: $("input[name='password-repeat']"),
        min_length: user_password_length,
        hints: $("div.password-hints *")
    });

});
