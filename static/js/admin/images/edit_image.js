$(document).ready(function() {

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
    photographer.typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: photographer.attr('data-source-url'),
                data: { name: query }
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

});
