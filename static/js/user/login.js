$(document).ready(function() {

    var login_wrapper = $("div.login-form-wrapper");
    var login_form = login_wrapper.find("form");

    Validator.validate({
        method: 'email',
        control_group: login_form.find("div.forgot-password-container div.control-group"),
        input: login_form.find("div.forgot-password-container input[name='email']"),
        req: true
    });

    /* Restore password */
    var forgot_password = login_wrapper.find("div.forgot-password");
    var restore_password_button = forgot_password.find("button.restore-password");
    var loader = forgot_password.find("img.ajaxloader");

    login_wrapper.find("a.forgot").click(function() {
        $(this).parent().hide();
        forgot_password.slideDown();
    });
    forgot_password.find("input[name='email']").keyup(function(e) {
        if(e.which == 13) { // Enter
            restore_password_button.click();
        }
    });
    restore_password_button.click(function() {
        forgot_password.find("div.alert").hide();
        restore_password_button.attr('disabled', true);
        loader.show();
        $.ajax({
            url: '/minside/gjenopprett-passord/e-post/',
            data: { email: forgot_password.find("input[name='email']").val() }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'unknown_email') {
                forgot_password.find("div.alert.unknown").show();
                restore_password_button.removeAttr('disabled');
            } else if(result.status == 'invalid_email') {
                forgot_password.find("div.alert.invalid").show();
                restore_password_button.removeAttr('disabled');
            } else if(result.status == 'unregistered_email') {
                forgot_password.find("div.alert.unregistered").show();
                restore_password_button.removeAttr('disabled');
            } else if(result.status == 'success') {
                forgot_password.find("div.alert.success").show();
            }
        }).fail(function(r) {
            forgot_password.find("div.alert.error").show();
            restore_password_button.removeAttr('disabled');
        }).always(function(r) {
            loader.hide();
        });
    });

});
