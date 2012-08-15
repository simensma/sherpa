/* Specific article-editing scripts */

$(document).ready(function() {

    $("select[name='authors']").select2({
        width: '350px'
    });

    $("article div.title").focusout(function() {
        $("a.header-title").text($(this).text());
    });

    $("input[name='article-datetime-field']").datetimepicker({
        dateFormat: "dd.mm.yy",
        seperator: " ",
        timeFormat: "hh:mm"
    });

    //carousel, stop spinning
    $('.carousel').each(function(){
        $(this).carousel({
            interval:false
        });
    });

    /* Publish/unpublish */
    function publishUnpublish(){
        try{
            var datetime = $("input[name='article-datetime-field']").datetimepicker('getDate');
            var now = new Date();
        }catch(e){
            var datetime = 0;
            var now = 0;
        }

        $("div.status h1.publish").empty();

        if($("div.status").attr("data-published").length > 0) {
            $("div.article button.publish").show();
            $("div.article button.unpublish").show();
            $("input[name='article-datetime-field']").show();
            if(datetime > now){
                $("div.status h1.publish").append("Artikkelen blir publisert <br>" + $("input[name='article-datetime-field']").val());
            }else{
                $("div.status h1.publish").append("Artikkelen er <span class='true'>publisert</span>");
                $("input[name='article-datetime-field']").val("")
            }
        } else {
            $("div.article button.publish").show();
            $("div.article button.unpublish").hide();
            $("input[name='article-datetime-field']").show();
            $("input[name='article-datetime-field']").val("")
            $("div.status h1.publish").append("Artikkelen er <span class='false'>ikke publisert</span>");
        }
    }
    publishUnpublish();

    $("div button.publish").click(function() {
        if(!confirm("Er du sikker på at du vil publisere denne artikkelen?")) {
            return;
        }
        setPublished(true, function() {
            $("div.status").attr("data-published", "true");
            publishUnpublish();
        });
    });

    $("div button.unpublish").click(function() {
        if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne artikkelen? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker. Du bør ikke avpublisere en publisert artikkel med mindre du er HELT sikker.")) {
            return;
        }
        setPublished(false, function() {
            $("div.status").attr("data-published", "");
            publishUnpublish();
        });
    });

    function setPublished(status, done) {
        $("div.status button.publish, div.status button.unpublish").attr('disabled', true);
        $.ajax({
            url: '/sherpa/artikler/publiser/' + $("div.editor-header").attr('data-id') + '/',
            data: {
                datetime : encodeURIComponent($("input[name='article-datetime-field']").val()),
                status : encodeURIComponent(JSON.stringify({'status': status}))
            }
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
            data: 'thumbnail=' + encodeURIComponent($("div.editor-header img.article-thumbnail").attr('src'))
        });
    }

    $("div.editor-header img.article-thumbnail").click(function() {
        var image = $(this);
        openImageDialog($(this), undefined, undefined, undefined, function(src, anchor, description, photographer) {
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
