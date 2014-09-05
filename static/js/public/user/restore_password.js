$(function() {
    Validator.validatePasswords({
        control_group: $("div.control-group.password, div.control-group.password-repeat"),
        pass1: $("input[name='password']"),
        pass2: $("input[name='password-repeat']"),
        min_length: Turistforeningen.user_password_length,
        hints: $("div.password-hint")
    });
});
