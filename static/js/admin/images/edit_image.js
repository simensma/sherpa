$(document).ready(function() {

    /* Tags */

    var tagger = new TypicalTagger($("input[name='tags']"), $("div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.tag").each(function() {
        tags.push($(this).text().trim().toLowerCase());
    });
    tagger.tags = tags;

    $("form.update-image").submit(function() {
        $("input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
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
