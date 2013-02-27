$(document).ready(function() {

    /* When creating a page, slugify the title as URL */
    $("#add-page-dialog input[name='title']").keyup(function() {
        $("#add-page-dialog input[name='slug']").val(slugify($(this).val()));
    });

    $("header select[name='user_association']").chosen().change(function() {
        var next = encodeURIComponent(location.pathname + location.search);
        var a = $('<a class="hide" href="' + $(this).find('option:selected').attr('data-href') + '?next=' + next + '">s</a>').appendTo(document.body).get(0).click();
    });
});

function slugify(string) {
    string = string.toLowerCase().trim();
    string = string.replace(/[^a-zæøåÆØÅ0-9-_\ ]/g, '')
    string = string.replace(/\ +/g, '-')
    return string.toLowerCase().trim();
}
