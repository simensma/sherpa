$(document).ready(function() {

    /* Ensure passwords are identical and long enough */
    $("form").submit(function(e) {
        if($(this).find("input[name='password']").val() != $(this).find("input[name='password-duplicate']").val()) {
            $("form div.control-group.password").addClass('error');
            $("form div.control-group.password-duplicate").addClass('error');
            addInfo("Passordene er ikke like!");
            e.preventDefault();
        } else if($(this).find("input[name='password']").val().length < password_length) {
            $("form div.control-group.password").addClass('error');
            $("form div.control-group.password-duplicate").addClass('error');
            addInfo("Passordet må være minst " + password_length + " tegn!");
            e.preventDefault();
        }
    });

    $("form input[type='password']").focus(function() {
        $("form input[type='password']").parents("div.control-group").removeClass('error');
    });

    function addInfo(header) {
        $("div.info-area").append('<div class="alert alert-danger"><a class="close">x</a><strong>' + header + '</strong></div>');
    }
});
