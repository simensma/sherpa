$(document).ready(function() {

    var form = $("form.fjelltreffen-annonse-edit");

    form.find("div.control-group.hideage div.controls a.hideage-info").click(function() {
        $(this).hide();
        form.find("div.control-group.hideage div.controls div.hideage-info").slideDown();
    });
    form.find("a.delete").click(function() {
        return confirm("Er du sikker på at du vil slette denne annonsen?");
    });

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

    var modal = $("div.annonse-image-modal");

    modal.find("button.delete-image").click(function() {
        if(!confirm("Er du sikker på at du vil slette bildet fra annonsen?")) {
            return $(this);
        }

        var url = $(this).attr("data-href");
        modal.find("p.delete").hide();
        modal.find("p.modal-close").hide();
        modal.find("p.loading").show();

        $.ajaxQueue({
            url: url
        }).done(function(result) {
            form.find("span.existing-image-label").hide();
            form.find("span.default-image-label").show();
            alert("Bildet har blitt slettet.");
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi prøvde å slette bildet. Vennligst prøv igjen senere.");
            modal.find("p.delete").show();
            modal.find("p.modal-close").show();
            modal.find("p.loading").hide();
        }).always(function(result) {
            modal.modal('hide');
        });
    });

});
