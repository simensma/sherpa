$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var input = form.find("div.tags input[name='tags']");

    form.find("div.control-group.start_date div.date,div.control-group.end_date div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        language: 'nb'
    });

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
