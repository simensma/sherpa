$(document).ready(function() {

    /* Ensure passwords are identical and long enough */
    $("form.password").submit(function(e) {
        if($(this).find("input[name='password']").val() != $(this).find("input[name='password-duplicate']").val()) {
            $("form div.control-group.password").addClass('error');
            $("form div.control-group.password-duplicate").addClass('error');
            addInfo("Passordene er ikke like!");
            //e.preventDefault();
        } else if($(this).find("input[name='password']").val().length > 0 && $(this).find("input[name='password']").val().length < password_length) {
            $("form div.control-group.password").addClass('error');
            $("form div.control-group.password-duplicate").addClass('error');
            addInfo("Passordet må være minst " + password_length + " tegn!");
            //e.preventDefault();
        }
    });

    $("form input").focus(function() {
        $(this).parents("div.control-group").removeClass('error');
    });

    $("form.password input[type='password']").focus(function() {
        $("form input[type='password']").parents("div.control-group").removeClass('error');
    });

    $("form input[name='name']").focusout(function() {
        if($(this).val().length == 0) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form input[name='email']").focusout(function() {
        if(!$(this).val().match(/.+@.+\..+/)) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form input[name='phone']").focusout(function() {
        if($(this).val().length > phone_max_length) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    function addInfo(header) {
        $("div.info-area").append('<div class="alert alert-danger"><a class="close">x</a><strong>' + header + '</strong></div>');
    }
});
