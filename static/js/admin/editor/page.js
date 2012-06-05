$(document).ready(function() {

    /* Automatically remove empty html contents */
    $(document).on('focusout', 'article div.html', function() {
        if($(this).text().trim() === "" && $(this).children("hr").length == 0) {
            $(this).addClass('empty');
            $(this).focus(function() {
                $(this).removeClass('empty');
            });
        }
    });
    $("article div.html").focusout();

    /* Publish/unpublish */

    if($("div.status[data-published]").length == 0) {
        $("div.status button.unpublish").hide();
    } else {
        $("div.status button.publish").hide();
    }

    $("div.status button.publish").click(function() {
        if(!confirm("Er du sikker på at du vil publisere denne siden?")) {
            return;
        }
        setPublished(true, function() {
            $("div.status h1.publish span.false").removeClass('false').addClass('true').text('publisert');
            $("div.status button.publish").hide();
            $("div.status button.unpublish").show();
        });
    });

    $("div.status button.unpublish").click(function() {
        if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne siden? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker.")) {
            return;
        }
        setPublished(false, function() {
            $("div.status h1.publish span.true").removeClass('true').addClass('false').text('ikke publisert');
            $("div.status button.publish").show();
            $("div.status button.unpublish").hide();
        });
    });

    function setPublished(status, done) {
        alert("Todo.");
    }

    /* Delete page */
    $("a.delete-page").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne siden, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

});
