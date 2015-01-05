/* Specific article-editing scripts */

$(function() {

    var header = $("div.editor-header");
    var editor = $("div.cms-editor");
    var article = editor.find("article");
    var delete_button = header.find('.delete-article');

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

    // Is use default image as article thumbnail preview checked?
    if (header.find('input[name="thumbnail"][value="default"][checked]').length > 0) {
        header.find('.article-thumbnail-preview.default').show();
        header.find('.article-thumbnail-preview.custom').hide();
    }

    // Is use custom image as article thumbnail preview checked?
    if (header.find('input[name="thumbnail"][value="custom"][checked]').length > 0) {
        header.find('.article-thumbnail-preview.default').hide();
        header.find('.article-thumbnail-preview.custom').show();
    }

    // Is use no article thumbnail preview checked?
    if (header.find('input[name="thumbnail"][value="none"][checked]').length > 0) {
        header.find('.article-thumbnail-preview.default').hide();
        header.find('.article-thumbnail-preview.custom').hide();
    }

    // When selecting use no article thumbnail
    header.find('input[name="thumbnail"][value="none"]').change(function() {
        if($(this).is(':checked')) {
            header.find('.article-thumbnail-preview').hide();
        }
    });

    // When selecting use default article thumbnail
    header.find("input[name='thumbnail'][value='default']").change(function(e) {
        if($(this).is(':checked')) {
            header.find('.article-thumbnail-preview.default').show();
            header.find('.article-thumbnail-preview.custom').hide();

            var $first_image = article.find('.content.image img').first();
            if (!!$first_image) {
                var first_image_url = $first_image.attr('src');
                header.find('.article-thumbnail-preview.default img').attr('src', first_image_url);
            }
        }
    });

    // When selecting use custom article thumbnail
    header.find("input[name='thumbnail'][value='new']").change(function() {
        if($(this).is(':checked')) {
            header.find('.article-thumbnail-preview.default').hide();
            header.find('.article-thumbnail-preview.custom').show();
        }
    });

    header.find("img.article-thumbnail").click(function() {
        var image = $(this);
        ImageDialog.open({
            src: image.attr('src'),
            anchor: '',
            description: '',
            photographer: '',
            save: function(src, anchor, description, photographer) {
                image.attr('src', src);
            },
        });
    });

    delete_button.on('click', function (e) {
        var delete_url = $(this).attr('data-dnt-redirect-url');
        location.href = delete_url;
    });

    // Init Tooltip
    header.find('.preview').tooltip();

});
