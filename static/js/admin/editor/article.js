/* Specific article-editing scripts */

$(document).ready(function() {

    var header = $("div.editor-header");

    header.find("select[name='authors']").chosen();

    header.find("div.publish div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    });

    //carousel, stop spinning
    $('.carousel').each(function(){
        $(this).carousel({
            interval:false
        });
    });

    /* Change thumbnail-image */
    if(header.find("input[name='thumbnail'][value='default'][checked]").length > 0 ||
        header.find("input[name='thumbnail'][value='none'][checked]").length > 0) {
        header.find("img.article-thumbnail").hide();
    }

    header.find("input[name='thumbnail'][value='none']").change(function() {
        if($(this).is(':checked')) {
            var image = $(this);
            header.find("img.article-thumbnail").hide();
            $.ajaxQueue({
                url: '/sherpa/nyheter/bilde/' + header.attr('data-article-id') + '/skjul/',
                type: 'POST'
            });
        }
    });

    header.find("input[name='thumbnail'][value='default']").change(function(e) {
        if($(this).is(':checked')) {
            if($("article div.image").length === 0) {
                alert("Det er ingen bilder i artikkelen å bruke som minibilde!");
                header.find("input[name='thumbnail'][value='none']").click();
                return;
            }
            var image = $(this);
            header.find("img.article-thumbnail").hide();
            $.ajaxQueue({
                url: '/sherpa/nyheter/bilde/' + header.attr('data-article-id') + '/slett/',
                type: 'POST'
            });
        }
    });

    header.find("input[name='thumbnail'][value='new']").change(function() {
        if($(this).is(':checked')) {
            var image = $(this);
            header.find("img.article-thumbnail").show();
            saveImage();
        }
    });

    function saveImage() {
        $.ajaxQueue({
            url: '/sherpa/nyheter/bilde/' + header.attr('data-article-id') + '/',
            data: { thumbnail: header.find("img.article-thumbnail").attr('src') }
        });
    }

    header.find("img.article-thumbnail").click(function() {
        var image = $(this);
        ImageDialog.openImageDialog({
            image: $(this),
            anchor: undefined,
            description: undefined,
            photographer: undefined,
            save: function(src, anchor, description, photographer) {
                image.attr('src', src);
                saveImage();
            },
            remove: function() {
                header.find("input[name='thumbnail'][value='none']").click();
            }
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
