/* Specific article-editing scripts */

$(function() {

    var editor = $("div.cms-editor");
    var header = editor.find("div.editor-header");
    var article = editor.find("article");

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
            header.find("img.article-thumbnail").hide();
        }
    });

    header.find("input[name='thumbnail'][value='default']").change(function(e) {
        if($(this).is(':checked')) {
            header.find("img.article-thumbnail").hide();
        }
    });

    header.find("input[name='thumbnail'][value='new']").change(function() {
        if($(this).is(':checked')) {
            header.find("img.article-thumbnail").show();
        }
    });

    header.find("img.article-thumbnail").click(function() {
        var image = $(this);
        ImageDialog.open({
            src: image.attr('src'),
            anchor: undefined,
            description: undefined,
            photographer: undefined,
            save: function(src, anchor, description, photographer) {
                image.attr('src', src);
            },
        });
    });

});
