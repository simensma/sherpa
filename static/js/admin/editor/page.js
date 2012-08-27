$(document).ready(function() {

    /* Publish/unpublish */

    if($("div.editor-header.page div.status[data-published]").length == 0) {
        $("div.editor-header.page div.status button.unpublish").hide();
    } else {
        $("div.editor-header.page div.status button.publish").hide();
    }

    $("div.editor-header.page div.status button.publish").click(function() {
        if(!confirm("Er du sikker på at du vil publisere denne siden?")) {
            return;
        }
        setPublished(true, function() {
            $("div.editor-header.page div.status h1.publish span.false").removeClass('false').addClass('true').text('publisert');
            $("div.editor-header.page div.status button.publish").hide();
            $("div.editor-header.page div.status button.unpublish").show();
        });
    });

    $("div.editor-header.page div.status button.unpublish").click(function() {
        if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne siden? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker.")) {
            return;
        }
        setPublished(false, function() {
            $("div.editor-header.page div.status h1.publish span.true").removeClass('true').addClass('false').text('ikke publisert');
            $("div.editor-header.page div.status button.publish").show();
            $("div.editor-header.page div.status button.unpublish").hide();
        });
    });

    function setPublished(status, done) {
        alert("Todo.");
    }

    /* Delete page */
    $("div.editor-header.page a.delete-page").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne siden, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

    /* Rename title */
    $("div.editor-header.page input[name='title']").focusout(function() {
        var title = $(this).val();
        $("div.editor-header.page span.title-status").hide();
        $(this).after('<img class="title-loader" src="/static/img/ajax-loader-small.gif" alt="Laster...">');
        debugger;
        $.ajax({
            url: '/sherpa/cms/side/tittel/' + $("div.editor-header.page").attr('data-id') + '/',
            data: 'title=' + encodeURIComponent(title)
        }).always(function() {
            $("div.editor-header.page img.title-loader").remove();
            $("div.editor-header.page span.title-status").show();
        });
    });

    /* Change parent */
    $("div.editor-header.page select[name='parent']").change(function() {
        var parent = $(this).find("option:selected").val();
        $("div.editor-header.page span.parent-status").hide();
        $(this).after('<img class="parent-loader" src="/static/img/ajax-loader-small.gif" alt="Laster...">');
        $.ajax({
            url: '/sherpa/cms/side/foreldre/' + $("div.editor-header.page").attr('data-id') + '/',
            data: 'parent=' + encodeURIComponent(parent)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'parent_in_parent') {
                alert('Du kan ikke velge den siden, fordi den allerede er en underside av denne siden.');
                $("div.editor-header.page select[name='parent']").val($("div.editor-header.page select[name='parent'] option.default").val());
            } else {
                $("div.editor-header.page select[name='parent'] option.default").removeClass('default');
                $("div.editor-header.page select[name='parent'] option:selected").addClass('default');
            }
        }).always(function() {
            $("div.editor-header.page img.parent-loader").remove();
            $("div.editor-header.page span.parent-status").show();
        });
    });

});
