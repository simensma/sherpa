$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var hide_aktivitet = form.find("div.control-group.hide_aktivitet");
    var tag_input = form.find("div.tags input[name='tag']");
    var tag_collection = form.find("div.tags input[name='tags']");
    var subcategories = form.find("select[name='subcategories']");

    form.find("div.control-group.difficulty select[name='difficulty']").chosen();
    subcategories.chosen();

    form.find("div.control-group.pub_date div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        language: 'nb'
    });

    // Sync subcategory-select with the actual chosen subcategories
    subcategories.change(function() {
        var option = subcategories.find("option:selected");
        // TODO should be an easier way to add the tag! Simulate typing it into the input for now.
        option.remove();
        subcategories.trigger('liszt:updated');
        tag_input.val(option.val());
        tag_input.focusout();
    });
    // TODO - re-add removed options on tag removal

    // Buttons without submit-type aren't supposed to submit the form
    $(document).on('click', "button:not([type='submit'])", function(e) {
        e.preventDefault();
    });

    var tagger = new TypicalTagger(tag_input, form.find("div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    form.find("div.tag-box div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    tagger.tags = tags;

    form.submit(function() {
        var hidden = hide_aktivitet.find("button.active").is(".hide_aktivitet");
        hide_aktivitet.find("input[name='hidden']").val(JSON.stringify(hidden));
        tag_collection.val(JSON.stringify(tagger.tags));
    });

});
