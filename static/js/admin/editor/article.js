/* Specific article-editing scripts */

$(document).ready(function() {
    $("article div.title").focusout(function() {
        $("a.header-title").text($(this).text());
    });

    /* Publish/unpublish */

    if($("div.status[data-published]").length == 0) {
        $("div.status button.unpublish").hide();
    } else {
        $("div.status button.publish").hide();
    }

    $("div.status button.publish").click(function() {
        if(!confirm("Er du sikker på at du vil publisere denne artikkelen?")) {
            return;
        }
        setPublished(true, function() {
            $("div.status h1.publish span.false").removeClass('false').addClass('true').text('publisert');
            $("div.status button.publish").hide();
            $("div.status button.unpublish").show();
        });
    });

    $("div.status button.unpublish").click(function() {
        if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne artikkelen? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker. Du bør ikke avpublisere en publisert artikkel med mindre du er HELT sikker.")) {
            return;
        }
        setPublished(false, function() {
            $("div.status h1.publish span.true").removeClass('true').addClass('false').text('ikke publisert');
            $("div.status button.publish").show();
            $("div.status button.unpublish").hide();
        });
    });

    function setPublished(status, done) {
        $("div.status button.publish, div.status button.unpublish").attr('disabled', true);
        $.ajax({
            url: '/sherpa/artikler/publiser/' + $("div.editor-header").attr('data-id') + '/',
            type: 'POST',
            data: 'status=' + encodeURIComponent(JSON.stringify({'status': status}))
        }).done(done).always(function() {
            $("div.status button.publish, div.status button.unpublish").removeAttr('disabled');
        });
    }


    /* Change thumbnail-image */

    if($("div.editor-header input[name='thumbnail'][value='default'][checked]").length > 0 ||
       $("div.editor-header input[name='thumbnail'][value='none'][checked]").length > 0) {
        $("div.editor-header img.article-thumbnail").hide();
    }

    $("div.editor-header input[name='thumbnail'][value='none']").change(function() {
        if($(this).is(':checked')) {
            var image = $(this);
            $("div.editor-header img.article-thumbnail").hide();
            $.ajax({
                url: '/sherpa/artikler/bilde/' + $("div.editor-header").attr('data-id') + '/skjul/',
                type: 'POST'
            });
        }
    });

    $("div.editor-header input[name='thumbnail'][value='default']").change(function(e) {
        if($(this).is(':checked')) {
            if($("article div.image").length == 0) {
                alert("Det er ingen bilder i artikkelen å bruke som minibilde!");
                $("div.editor-header input[name='thumbnail'][value='none']").click();
                return;
            }
            var image = $(this);
            $("div.editor-header img.article-thumbnail").hide();
            $.ajax({
                url: '/sherpa/artikler/bilde/' + $("div.editor-header").attr('data-id') + '/slett/',
                type: 'POST'
            });
        }
    });

    $("div.editor-header input[name='thumbnail'][value='new']").change(function() {
        if($(this).is(':checked')) {
            var image = $(this);
            $("div.editor-header img.article-thumbnail").show();
            saveImage();
        }
    });

    function saveImage() {
        $.ajax({
            url: '/sherpa/artikler/bilde/' + $("div.editor-header").attr('data-id') + '/',
            type: 'POST',
            data: 'thumbnail=' + encodeURIComponent($("div.editor-header img.article-thumbnail").attr('src'))
        });
    }

    $("div.editor-header img.article-thumbnail").click(function() {
        var image = $(this);
        openImageDialog($(this).attr('src'), undefined, undefined, undefined, function(src, anchor, alt) {
            image.attr('src', src);
            saveImage();
        }, function() {
            $("div.editor-header input[name='thumbnail'][value='none']").click();
        });
    });

    /* Delete article */
    $("a.delete-article").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne artikkelen, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

    /* Mark empty text elements */
    $(document).on('focusout', 'div.editable', markEmptyContent);
    $("div.editable").each(markEmptyContent);
    function markEmptyContent() {
        if($(this).text().trim() === "") {
            $(this).addClass('selected');
        } else {
            $(this).removeClass('selected');
        }
    }

});
