$(function() {

    /* When creating a page, slugify the title as URL */
    $("#add-page-dialog input[name='title']").keyup(function() {
        $("#add-page-dialog input[name='slug']").val(slugify($(this).val()));
    });

    $("select[name='user_forening']").chosen().change(function() {
        var next = encodeURIComponent(location.pathname + location.search);
        var a = $('<a class="jq-hide" href="' + $(this).find('option:selected').attr('data-href') + '?next=' + next + '">s</a>').appendTo(document.body).get(0).click();
    });

    // Toggle dropdowns in the main admin menu
    var nav = $("nav.navbar ul.nav");
    nav.find("li a[data-toggle]").click(function() {
        nav.find("li[data-type='" + $(this).attr('data-toggle') + "']").slideToggle('fast');
    });

});

function slugify(string) {
    string = string.toLowerCase().trim();
    string = string.replace(/[^a-zæøåÆØÅ0-9-_\ ]/g, '');
    string = string.replace(/\ +/g, '-');
    return string.toLowerCase().trim();
}
