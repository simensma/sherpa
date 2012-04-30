/* Specific article-editing scripts */

$(document).ready(function() {
    $("div[data-type='title']").focusout(function() {
        $("a.header-title").text($(this).text());
    });

    /* Publish/unpublish */

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
            url: '/sherpa/artikler/publiser/' + $(this).parents("div.edit-article-header").attr('data-id') + '/',
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

    /* Change thumbnail-image */

    if($("div.edit-article-header input[name='thumbnail'][value='default'][checked]").length > 0) {
        $("div.edit-article-header img.article-thumbnail").hide();
    }

    $("div.edit-article-header input[name='thumbnail'][value='default']").click(function() {
        if($(this).is(':checked')) {
            chooseImage(true);
        } else {
            chooseImage(false);
        }
    });

    $("div.edit-article-header input[name='thumbnail'][value='new']").click(function() {
        if($(this).is(':checked')) {
            chooseImage(false);
        } else {
            chooseImage(true);
        }
    });

    function chooseImage(original) {
        var image = $(this);
        if(original) {
            $("div.edit-article-header img.article-thumbnail").hide();
            $.ajax({
                url: '/sherpa/artikler/bilde/' + $("div.edit-article-header").attr('data-id') + '/slett/',
                type: 'POST'
            });
        } else {
            $("div.edit-article-header img.article-thumbnail").show();
            saveImage();
        }
    }

    function saveImage() {
        $.ajax({
            url: '/sherpa/artikler/bilde/' + $("div.edit-article-header").attr('data-id') + '/',
            type: 'POST',
            data: 'thumbnail=' + encodeURIComponent($("div.edit-article-header img.article-thumbnail").attr('src'))
        });
    }

    $("div.edit-article-header img.article-thumbnail").click(function() {
        var image = $(this);
        openImageDialog($(this).attr('src'), '', '', function(src, anchor, alt) {
            image.attr('src', src);
            saveImage();
        });
    });

    /* Delete article */
    $("a.delete-article").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne artikkelen, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

});
