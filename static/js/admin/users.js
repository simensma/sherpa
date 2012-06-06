$(document).ready(function() {

    /* Suggest username based on name */
    $("form input[name='name']").keyup(function() {
        var suggestedUsername = '';
        var names = $(this).val().split(' ');
        suggestedUsername += names[0];
        if(names.length > 1) {
            for(var i=1; i<names.length; i++) {
                suggestedUsername += names[i].substring(0, 1);
            }
        }

        $("form input[name='username']").val(suggestedUsername.toLowerCase());
    });

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
