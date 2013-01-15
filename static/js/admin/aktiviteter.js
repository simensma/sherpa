$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var input = form.find("div.tags input[name='tags']");

    var tagger = new TypicalTagger(input, form.find("div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    form.find("div.tag-box div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    tagger.tags = tags;

    form.submit(function() {
        input.val(JSON.stringify(tagger.tags));
    });

});
