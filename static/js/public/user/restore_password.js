$(function() {
    Validator.validatePasswords({
        form_group: $('[data-dnt-form-group="password"], [data-dnt-form-group="password-repeat"]'),
        pass1: $('input[name="password"]'),
        pass2: $('input[name="password-repeat"]'),
        min_length: Turistforeningen.user_password_length,
        help_blocks: $('.password-hint')
    });
});
