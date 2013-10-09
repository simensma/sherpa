$(document).ready(function() {

    var wrapper = $("div.registration-form-nonmember-wrapper");
    var confirmation = wrapper.find("a.confirm");
    var form_wrapper = wrapper.find("div.form-wrapper");
    var form = wrapper.find("form.registration-nonmember");

    confirmation.click(function() {
        $(this).parents("div.alert").hide();
        form_wrapper.fadeIn();
    });

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

    Validator.validatePasswords({
        control_group: form.find("div.control-group.password, div.control-group.password-repeat"),
        pass1: form.find("input[name='password']"),
        pass2: form.find("input[name='password-repeat']"),
        min_length: Turistforeningen.user_password_length,
        hints: form.find("div.form-elements div.password-hint")
    });

});
