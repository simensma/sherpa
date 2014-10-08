$(function() {

    /* Tags */

    TagDisplay.enable({
        targetInput: $("input[name='tags-serialized']"),
        tagBox: $("div.tag-box"),
        pickerInput: $("input[name='tags']")
    });

    $("form.update-image").submit(function() {
        TagDisplay.collect();
    });

    var photographer = $("form.update-image input[name='photographer']");
    SimpleTypeahead({
        url: photographer.attr('data-photographers-url'),
        $input: photographer,
    });

});
