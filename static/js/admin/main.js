$(function() {

    // Simulate anchor click when user changes active forening
    $("select[name='user_forening']").chosen().change(function() {
        var a = $('<a class="jq-hide" href="' + $(this).find('option:selected').attr('data-href') + '">s</a>').appendTo(document.body).get(0).click();
    });

    // Toggle dropdowns in the main admin menu
    var nav = $("nav.navbar ul.nav");
    nav.find("[data-toggle]").click(function(e) {
        // This element is expected to be contained within an anchor, and we want to prevent the anchor click if the
        // toggler was clicked.
        e.preventDefault();

        nav.find("li[data-type='" + $(this).attr('data-toggle') + "']").slideToggle('fast');
    });

    // Activate outdatedBrowser warning
    outdatedBrowser({
        bgColor: '#f25648',
        color: '#ffffff',
        lowerThan: 'IE9'
    });

});
