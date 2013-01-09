$(document).ready(function() {
    
    var annonseid = $("div.annonse").attr("data-id");

    $("button.annonsereply-send").click(function(){
        console.log("dkjsl");
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

        var namecontrol = $("input.annonsereply-name-control");
        var emailcontrol = $("input.annonsereply-email-control");
        var text = $("textarea.annonsereply-text");

        //simple client-side validation, proper validation is performed server-side
        if(namecontrol.hasClass("error")){
            alert("Du må ha en tittel!");
            enableButtons();
            return;
        }
        if(emailcontrol.hasClass("error")){
            alert("Du må skrive inn en epostadresse, uten denne kan ikke annonsøren svare deg!");
            enableButtons();
            return;
        }
        if(text.val().length <= 3){
            alert("Skal du virkelig sende et så kort svar?");
            enableButtons();
            return;
        }

        content = {
            id:annonseid,
            name:$("input.annonsereply-name").val(),
            email:$("input.annonsereply-email").val(),
            text:$("textarea.annonsereply-text").val(),
        }
        console.log(content);
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