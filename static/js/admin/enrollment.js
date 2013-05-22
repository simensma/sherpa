$(document).ready(function() {

    var enrollment = $("div.change-enrollment-status");

    function activateState(state) {
        enrollment.find("p.ajaxloader.state").show();
        $.ajaxQueue({
            url: enrollment.attr('data-activate-state-url'),
            data: { active: JSON.stringify(state) }
        }).done(function() {
            enrollment.find("div.active.state").toggle();
            enrollment.find("div.inactive.state").toggle();
        }).fail(function() {
            alert("Asynkron kommunikasjon med serveren feilet! Er du sikker på at du har nettilgang?\n\nI så fall, prøv igjen litt senere.");
        }).always(function() {
            enrollment.find("p.ajaxloader.state").hide();
        });
    }

    function activateCard(state) {
        enrollment.find("p.ajaxloader.card").show();
        $.ajaxQueue({
            url: enrollment.attr('data-activate-card-url'),
            data: { card: JSON.stringify(state) }
        }).done(function() {
            enrollment.find("div.active.card").toggle();
            enrollment.find("div.inactive.card").toggle();
        }).fail(function() {
            alert("Asynkron kommunikasjon med serveren feilet! Er du sikker på at du har nettilgang?\n\nI så fall, prøv igjen litt senere.");
        }).always(function() {
            enrollment.find("p.ajaxloader.card").hide();
        });
    }

    enrollment.find("button.activate-state").click(function() {
        if(confirm("Er du sikker på at du vil reaktivere innmeldingsskjemaet?")) {
            activateState(true);
        }
    });

    enrollment.find("button.deactivate-state").click(function() {
        if(confirm("Er du helt sikker på at du vil deaktivere innmeldingsskjemaet?")) {
            activateState(false);
        }
    });

    enrollment.find("button.activate-card").click(function() {
        if(confirm("Er du sikker på at du vil reaktivere kortbetaling?")) {
            activateCard(true);
        }
    });

    enrollment.find("button.deactivate-card").click(function() {
        if(confirm("Er du helt sikker på at du vil deaktivere kortbetaling?")) {
            activateCard(false);
        }
    });
});
