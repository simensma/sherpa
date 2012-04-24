/* Editing an article (not its contents) */

$(document).ready(function() {

    $("div.published:not([data-active])").hide();

    $("div.published button.publish").click(function() {
        if($("div.published.true[data-active]").length == 0) {
            if(!confirm("Er du sikker på at du vil publisere den aktive versjonen for denne artikkelen?")) {
                return;
            }
        } else {
            if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne artikkelen? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker. Du bør ikke avpublisere en publisert artikkel med mindre du er HELT sikker.")) {
                return;
            }
        }
        var button = $(this);
        button.attr('disabled', true);
        $.ajax({
            url: '/sherpa/artikler/publiser/' + $(this).attr('data-id') + '/',
            type: 'POST'
        }).done(function() {
            var active = $("div.published[data-active]");
            var inactive = $("div.published:not([data-active])");
            active.removeAttr('data-active').hide();
            inactive.attr('data-active', true).show();
        }).always(function() {
            button.removeAttr('disabled');
        });
    });

});
