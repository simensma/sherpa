$(document).ready(function() {

    $("table.multiple-metadata button.new, table.multiple-metadata button.keep").click(function(e) {
        e.preventDefault();
        $(this).toggle();
        $(this).siblings("button.keep, button.new").toggle();
        $(this).parents("td").siblings("td.new").toggle();
        $(this).parents("td").siblings("td.keep").toggle();
    });

    TagDisplay.enable({
        targetInput: $("input[name='tags-serialized']"),
        tagBox: $("div.tag-box"),
        pickerInput: $("input[name='tags']")
    });

    $("form.update-images").submit(function() {
        TagDisplay.collect();
        var fields = {
            description: $("table.multiple-metadata tr.description button.new:hidden").length > 0,
            photographer: $("table.multiple-metadata tr.photographer button.new:hidden").length > 0,
            credits: $("table.multiple-metadata tr.credits button.new:hidden").length > 0,
            licence: $("table.multiple-metadata tr.licence button.new:hidden").length > 0
        };
        $("input[name='fields']").val(JSON.stringify(fields));
    });

    var photographer = $("form.update-images input[name='photographer']");
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
