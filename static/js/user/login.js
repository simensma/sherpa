$(document).ready(function() {

    /* Restore password */
    var forgot_password = $("div.forgot-password");
    $("div#login a.forgot").click(function() {
        $(this).parent().hide();
        forgot_password.slideDown();
    });
    forgot_password.find("input[name='email']").keyup(function(e) {
        if(e.which == 13) { // Enter
            forgot_password.find("button.restore-password").click();
        }
    });
    forgot_password.find("button.restore-password").click(function() {
        forgot_password.find("p.info").hide();
        var button = $(this);
        button.attr('disabled', true);
        $("img.ajaxloader").show();
        $.ajax({
            url: '/minside/gjenopprett-passord/e-post/',
            data: 'email=' + encodeURIComponent(forgot_password.find("input[name='email']").val())
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'unknown_email') {
                forgot_password.find("p.info.unknown").show();
                button.removeAttr('disabled');
            } else if(result.status == 'invalid_email') {
                forgot_password.find("p.info.invalid").show();
                button.removeAttr('disabled');
            } else if(result.status == 'success') {
                forgot_password.find("p.info.success").show();
            }
        }).fail(function(r) {
            forgot_password.find("p.info.error").show();
            button.removeAttr('disabled');
            button.text(button.attr('data-original-text'));
        }).always(function(r) {
            $("img.ajaxloader").hide();
        });
    });

});
