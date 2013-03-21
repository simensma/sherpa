$(document).ready(function() {

    Validator.validate({
        method: 'email',
        control_group: $("div.forgot-password-container div.control-group"),
        input: $("div.forgot-password-container input[name='email']"),
        req: true
    });

    /* Restore password */
    var forgot_password = $("div.forgot-password");
    var button = forgot_password.find("button.restore-password");
    var loader = forgot_password.find("img.ajaxloader");

    $("a.forgot").click(function() {
        $(this).parent().hide();
        forgot_password.slideDown();
    });
    forgot_password.find("input[name='email']").keyup(function(e) {
        if(e.which == 13) { // Enter
            forgot_password.find("button.restore-password").click();
        }
    });
    button.click(function() {
        forgot_password.find("p.info").hide();
        button.attr('disabled', true);
        loader.show();
        $.ajax({
            url: '/minside/gjenopprett-passord/e-post/',
            data: { email: forgot_password.find("input[name='email']").val() }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'unknown_email') {
                forgot_password.find("p.info.unknown").show();
                button.removeAttr('disabled');
            } else if(result.status == 'invalid_email') {
                forgot_password.find("p.info.invalid").show();
                button.removeAttr('disabled');
            } else if(result.status == 'unregistered_email') {
                forgot_password.find("p.info.unregistered").show();
                button.removeAttr('disabled');
            } else if(result.status == 'success') {
                forgot_password.find("p.info.success").show();
            }
        }).fail(function(r) {
            forgot_password.find("p.info.error").show();
            button.removeAttr('disabled');
        }).always(function(r) {
            loader.hide();
        });
    });

});
