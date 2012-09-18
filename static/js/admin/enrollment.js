$(document).ready(function() {
    function activateState(state) {
        $("p.ajaxloader.state").show();
        $.ajaxQueue({
            url: '/sherpa/innmelding/aktiver/innmelding/',
            data: 'active=' + encodeURIComponent(JSON.stringify(state))
        }).done(function() {
            $("div.active.state").toggle();
            $("div.inactive.state").toggle();
        }).fail(function() {
            alert("Asynkron kommunikasjon med serveren feilet! Er du sikker på at du har nettilgang?\n\nI så fall, prøv igjen litt senere.");
        }).always(function() {
            $("p.ajaxloader.state").hide();
        });
    }

    function activateCard(state) {
        $("p.ajaxloader.card").show();
        $.ajaxQueue({
            url: '/sherpa/innmelding/aktiver/kort/',
            data: 'card=' + encodeURIComponent(JSON.stringify(state))
        }).done(function() {
            $("div.active.card").toggle();
            $("div.inactive.card").toggle();
        }).fail(function() {
            alert("Asynkron kommunikasjon med serveren feilet! Er du sikker på at du har nettilgang?\n\nI så fall, prøv igjen litt senere.");
        }).always(function() {
            $("p.ajaxloader.card").hide();
        });
    }

    $("button.activate-state").click(function() {
        if(confirm("Er du sikker på at du vil reaktivere innmeldingsskjemaet?")) {
            activateState(true);
        }
    });

    $("button.deactivate-state").click(function() {
        if(confirm("Er du helt sikker på at du vil deaktivere innmeldingsskjemaet?")) {
            activateState(false);
        }
    });

    $("button.activate-card").click(function() {
        if(confirm("Er du sikker på at du vil reaktivere kortbetaling?")) {
            activateCard(true);
        }
    });

    $("button.deactivate-card").click(function() {
        if(confirm("Er du helt sikker på at du vil deaktivere kortbetaling?")) {
            activateCard(false);
        }
    });
});
