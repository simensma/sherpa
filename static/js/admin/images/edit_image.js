$(document).ready(function() {

    /* Tags */

    var tagger = new TypicalTagger($("input[name='tags']"), $("div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    $("div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    tagger.tags = tags;

    // Add events to the tag remover button
    $(document).on('mouseover', 'div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-hover.png');
    });
    $(document).on('mouseout', 'div.tag-box div.tag a', function() {
        $(this).children("img").attr('src', '/static/img/so/close-default.png');
    });
    $(document).on('click', 'div.tag-box div.tag a', function() {
        tagger.removeTag($(this).parent().text().trim());
        $(this).parent().remove();
    });

    $("form.update-image").submit(function() {
        $("input[name='tags-serialized']").val(JSON.stringify(tagger.tags));
    });

    $("form.update-image input[name='photographer']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/fotograf/',
                data: 'name=' + encodeURIComponent(query)
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });

});
