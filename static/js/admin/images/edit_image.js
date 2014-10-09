$(function() {

    /* Tags */

    Select2Tagger({$input: $('form.update-image input[name="tags"]')});

    var photographer = $("form.update-image input[name='photographer']");
    SimpleTypeahead({
        url: photographer.attr('data-photographers-url'),
        $input: photographer,
    });

});
