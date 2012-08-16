/* Specific article-editing scripts */

$(document).ready(function() {

    $("select[name='authors']").select2({
        width: '400px'
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
        if(!confirm("Er du sikker på at du vil slette denne artikkelen for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.")) {
            e.preventDefault();
        }
    });

    $("button.confirm-delete").click(function() {
        $(this).hide();
        $("div.final-confirm").show();
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
