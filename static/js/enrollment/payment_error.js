$(document).ready(function() {
    var refresh_button = $("a.refresh");
    var what_to_do_anchor = $("p.help-action.what-to-do a");
    var more_information_anchor = $("p.help-action.more-information a");
    var what_to_do_div = $("div.what-to-do");
    var more_information_div = $("div.more-information");

    refresh_button.click(function() {
        document.location.reload(true);
    });

    what_to_do_anchor.click(function() {
        $(this).parent().hide();
        what_to_do_div.slideDown();
    });

    more_information_anchor.click(function() {
        $(this).parent().hide();
        more_information_div.slideDown();
    });
});
