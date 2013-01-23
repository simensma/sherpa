$(document).ready(function() {

    var form = $("form.fjelltreffen-annonse-edit");

    form.find("p.hide-annonse").tooltip();

    Validator.validate({
        method: 'anything',
        control_group: form.find("div.control-group.title"),
        input: form.find("input[name='title']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: form.find("div.control-group.email"),
        input: form.find("input[name='email']"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: form.find("div.control-group.text"),
        input: form.find("textarea[name='text']"),
        req: true
    });

    form.submit(function(e) {
        // Recheck upon submit, because checks server-side causes loss of submitted info.
        // It might suck for a novice user to submit an invalid email address and lose a long post.
        // Just use the error class on the control-groups to determine if stuff is valid.
        // These error messages are duplicated in the messages from server-side validations.

        if(form.find("div.control-group.title").is(".error")) {
            alert("Du må fylle inn en tittel på annonsen.");
            e.preventDefault();
        }

        if(form.find("div.control-group.email").is(".error")) {
            alert("Du må fylle inn en gyldig e-postadresse!\n\n" +
                "Du vil motta svar på annonsen på denne adressen. Adressen vises ikke i annonsen.");
            e.preventDefault();
        }

        if(form.find("div.control-group.text").is(".error")) {
            alert("Du får neppe napp med mindre du skriver litt om hvem du er, eller hva du er ute etter, i annonsen.");
            e.preventDefault();
        }
    });

});
