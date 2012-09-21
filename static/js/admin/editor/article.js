/* Specific article-editing scripts */

$(document).ready(function() {

    $("select[name='authors']").chosen();

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

    /* Tags */

    // Create the tagger object, make it globally accessible (save.js will use this)
    window.article_tagger = new Tagger($("div.editor-header div.tags input[name='tags']"), function(tag) {
        // New tag added
        var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + tag + '</div>');
        $("div.tag-box").append(tag);
    }, function(tag) {
        // Existing tag
        $("div.tag-box div.tag").each(function() {
            if($(this).text().trim().toLowerCase() == tag.toLowerCase()) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
            }
        });
    });

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.editor-header div.tags div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    article_tagger.tags = tags;

    // Add events to the tag remover button
    $(document).on('mouseover', 'div.editor-header div.tags div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-hover.png');
    });
    $(document).on('mouseout', 'div.editor-header div.tags div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-default.png');
    });
    $(document).on('click', 'div.editor-header div.tags div.tag-box div.tag a', function() {
        article_tagger.removeTag($(this).parent().text().trim());
        $(this).parent().remove();
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
                url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-id') + '/skjul/',
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
                url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-id') + '/slett/',
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
            url: '/sherpa/nyheter/bilde/' + $("div.editor-header").attr('data-id') + '/',
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
