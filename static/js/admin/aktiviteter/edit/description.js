$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var hide_aktivitet = form.find("div.control-group.hide_aktivitet");
    var tag_input = form.find("div.tags input[name='tag']");
    var tag_collection = form.find("div.tags input[name='tags']");
    var subcategories = form.find("select[name='subcategories']");
    var association_select = form.find("select[name='association']");
    var co_association_select = form.find("select[name='co_association']");
    var images = form.find("input[name='images']");

    association_select.chosen();
    co_association_select.chosen({
        'allow_single_deselect': true
    });

    form.find("div.control-group.difficulty select[name='difficulty']").chosen();
    form.find("div.control-group.audiences select[name='audiences']").chosen();
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

    TagDisplay.enable({
        targetInput: tag_collection,
        tagBox: form.find("div.tag-box"),
        pickerInput: tag_input
    });

    form.submit(function() {
        var hidden = hide_aktivitet.find("button.active").is(".hide_aktivitet");
        hide_aktivitet.find("input[name='hidden']").val(JSON.stringify(hidden));
        TagDisplay.collect();
        images.val(JSON.stringify(ImageCarouselPicker.getImages()));
    });

});
