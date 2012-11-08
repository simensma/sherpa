/* Specific article-editing scripts */

$(document).ready(function() {

    $("select[name='authors']").chosen();

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

    /* Tags */

    // Create the tagger object, make it globally accessible (save.js will use this)
    window.article_tagger = new TypicalTagger($("div.editor-header div.tags input[name='tags']"), $("div.editor-header div.tags div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.editor-header div.tags div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    article_tagger.tags = tags;

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
                url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-article-id') + '/skjul/',
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
                url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-article-id') + '/slett/',
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
            url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-article-id') + '/',
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
