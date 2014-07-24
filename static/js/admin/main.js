$(function() {

    // Simulate anchor click when user changes active forening
    $("select[name='user_forening']").chosen().change(function() {
        var a = $('<a class="jq-hide" href="' + $(this).find('option:selected').attr('data-href') + '">s</a>').appendTo(document.body).get(0).click();
    });

    // Toggle dropdowns in the main admin menu
    var nav = $("nav.navbar ul.nav");
    nav.find("li a[data-toggle]").click(function() {
        nav.find("li[data-type='" + $(this).attr('data-toggle') + "']").slideToggle('fast');
    });

});
