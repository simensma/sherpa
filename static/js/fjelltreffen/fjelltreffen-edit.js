$(document).ready(function() {

    var annonseid = $("div.annonse").attr("data-id");

    $("button.save-annonse").click(function(){
        disableButtons();
        saveAnnonse();
    });
    $("button.delete-annonse").click(function(){
        disableButtons();
        deleteAnnonse();
    });

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.annonse-email-control"),
        input: $("input.annonse-email"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.annonse-title-control"),
        input: $("input.annonse-title"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.annonse-text-control"),
        input: $("textarea.annonse-text"),
        req: true
    });

    function deleteAnnonse(){
        $.ajaxQueue({
            url: '/fjelltreffen/slett/' + annonseid + "/",
        }).done(function(result) {
            window.location.href = "http://www.turistforeningen.no/fjelltreffen/mine";
        }).fail(function(result) {
            alert("Det skjedde en feil under sletting av annonsen, sjekk at du er koblet til internet eller prøv igjen senere.");
            enableButtons();
        }).always(function() {

        });
    }

    function saveAnnonse(){

        var titlecontrol = $("input.annonse-title-control");
        var emailcontrol = $("input.annonse-email-control");
        var text = $("textarea.annonse-text");

        //simple client-side validation, proper validation is performed server-side
        if(titlecontrol.hasClass("error")){
            alert("Du må ha en tittel!");
            enableButtons();
            return;
        }
        if(emailcontrol.hasClass("error")){
            alert("Du må skrive inn en epostadresse, svar vil bli sendt til denne adressen!");
            enableButtons();
            return;
        }
        if(text.val().length <= 10){
            alert("Du får neppe napp med en så kort annonse!");
            enableButtons();
            return;
        }

        content = {
            id:annonseid,
            hidden:$("input.annonse-hide").prop("checked"),
            hideage:$("input.annonse-hideage").prop("checked"),
            title:$("input.annonse-title").val(),
            email:$("input.annonse-email").val(),
            text:$("textarea.annonse-text").val(),
            fylke:$("select.annonse-fylke").val()
        }
        $.ajaxQueue({
            url: '/fjelltreffen/lagre/',
            data: 'annonse=' + JSON.stringify(content)
        }).done(function(result) {
            returnedData = JSON.parse(result);
            annonseid = returnedData['id'];
            window.location = "/fjelltreffen/mine/";
        }).fail(function(result) {
            try{
                returnedData = JSON.parse(result['responseText']);
                if (returnedData['error'] == 'toomany'){
                    alert("Du har for mange aktive annonser! Du kan ha max " + returnedData['num'] + " synlige annonser av gangen. Du kan slette eller skjule annonser under mine annonser. Du kan også lagre denne annonsen hvis du velger å skjule den, så mister du ikke det du har skrevet.");
                }
            }catch(err){
                alert("Det skjedde en feil under lagring av annonsen, sjekk at feltene er fylt ut riktig og at du er koblet til internet.");
            }
        }).always(function() {
            enableButtons();
        });

    }

    function disableButtons(){
        $("button.save-annonse").attr("disabled", true)
        $("button.delete-annonse").attr("disabled", true)
    }

    function enableButtons(){
        $("button.save-annonse").attr("disabled", false)
        $("button.delete-annonse").attr("disabled", false)
    }
});
