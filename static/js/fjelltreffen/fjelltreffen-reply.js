$(document).ready(function() {
    
    var annonseid = $("div.annonse").attr("data-id");

    $("button.annonsereply-send").click(function(){
        disableButtons();
        reply();
    });

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.annonsereply-email-control"),
        input: $("input.annonsereply-email"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.annonsereply-name-control"),
        input: $("input.annonsereply-name"),
        req: true
    });

    function reply(){

        var name = $("input.annonsereply-name");
        var email = $("input.annonsereply-email");
        var namecontrol = $("div.annonsereply-name-control");
        var emailcontrol = $("div.annonsereply-email-control");
        var text = $("textarea.annonsereply-text");

        //simple client-side validation, proper validation is performed server-side
        if(namecontrol.hasClass("error") || name.val().length < 1){
            alert("Du må ha et navn!");
            enableButtons();
            return;
        }
        if(emailcontrol.hasClass("error") || email.val().length < 3){
            alert("Du må skrive inn en epostadresse, uten denne kan ikke annonsøren svare deg!");
            enableButtons();
            return;
        }
        if(text.val().length <= 5){
            alert("Du må skrive et litt lengere svar!");
            enableButtons();
            return;
        }

        content = {
            id:annonseid,
            name:name.val(),
            email:email.val(),
            text:text.val(),
        }
        
        $.ajaxQueue({
            url: '/fjelltreffen/reply/',
            data: 'reply=' + JSON.stringify(content)
        }).done(function(result) {
            alert("Ditt svar har blitt sendt til annonsøren.");
            location.reload();
        }).fail(function(result) {
            alert("Det skjedde en feil under sendig av svar, har du fylt inn feltene riktig og er koblet til internet? Det kan også hende at det er noe galt med eposten til annonsøren.");
            enableButtons();
        });
    }

    function disableButtons(){
        $("button.annonsereply-send").attr("disabled", true)
    }

    function enableButtons(){
        $("button.annonsereply-send").attr("disabled", false)
    }
});