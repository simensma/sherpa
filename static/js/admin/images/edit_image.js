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

    $("form.update-image input[name='photographer']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/fotograf/',
                data: { name: query }
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

});
