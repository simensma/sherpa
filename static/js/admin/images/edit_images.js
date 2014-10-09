$(function() {

    $("table.multiple-metadata button.new, table.multiple-metadata button.keep").click(function(e) {
        e.preventDefault();
        $(this).toggle();
        $(this).siblings("button.keep, button.new").toggle();
        $(this).parents("td").siblings("td.new").toggle();
        $(this).parents("td").siblings("td.keep").toggle();
    });

    Select2Tagger({$input: $('input[name="tags"]')});

    $("form.update-images").submit(function() {
        var fields = {
            description: $("table.multiple-metadata tr.description button.new:hidden").length > 0,
            photographer: $("table.multiple-metadata tr.photographer button.new:hidden").length > 0,
            credits: $("table.multiple-metadata tr.credits button.new:hidden").length > 0,
            licence: $("table.multiple-metadata tr.licence button.new:hidden").length > 0
        };
        $("input[name='fields']").val(JSON.stringify(fields));
    });

    var photographer = $("form.update-images input[name='photographer']");
    SimpleTypeahead({
        url: photographer.attr('data-photographers-url'),
        $input: photographer,
    });

});
