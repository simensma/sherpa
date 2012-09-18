$(document).ready(function() {
    function activate(state) {
        $("p.ajaxloader").show();
        $.ajaxQueue({
            url: '/sherpa/innmelding/aktiver/',
            data: 'active=' + encodeURIComponent(state)
        }).done(function() {
            $("div.active").toggle();
            $("div.inactive").toggle();
        }).fail(function() {
            alert("Asynkron kommunikasjon med serveren feilet! Er du sikker på at du har nettilgang?\n\nI så fall, prøv igjen litt senere.");
        }).always(function() {
            $("p.ajaxloader").hide();
        });
    }

    $("button.activate").click(function() {
        activate(true);
    });

    $("button.deactivate").click(function() {
        activate(false);
    });
});
