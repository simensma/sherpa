$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var signup_enabled = form.find("div.control-group.signup_enabled");
    var hide_aktivitet = form.find("div.control-group.hide_aktivitet");
    var signup_details = form.find("div.signup-details");
    var input = form.find("div.tags input[name='tags']");

    // Long selectors make you feel alive
    form.find("div.control-group.start_date div.date,div.control-group.end_date div.date,div.control-group.signup_start div.date,div.control-group.signup_deadline div.date,div.control-group.signup_cancel_deadline div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        language: 'nb'
    });

    // Hide signup-options if signup is disabled
    signup_enabled.find("button").click(function() {
        if($(this).is(".enable")) {
            signup_details.slideDown();
            signup_enabled.find("input[name='signup_enabled']").val(JSON.stringify(true));
        } else if($(this).is(".disable")) {
            signup_details.slideUp();
            signup_enabled.find("input[name='signup_enabled']").val(JSON.stringify(false));
        }
    });

    // Buttons in button-groups aren't submit-buttons
    form.find("div.btn-group button").click(function(e) {
        e.preventDefault();
    });

    var tagger = new TypicalTagger(input, form.find("div.tag-box"));

    // Collect existing tags based on the DOM and layout
    var tags = [];
    form.find("div.tag-box div.tag").each(function() {
        tags.push($(this).text().trim());
    });
    tagger.tags = tags;

    form.submit(function() {
        var hidden = hide_aktivitet.find("button.active").is(".hide_aktivitet");
        hide_aktivitet.find("input[name='hidden']").val(JSON.stringify(hidden));
        input.val(JSON.stringify(tagger.tags));
    });

});
