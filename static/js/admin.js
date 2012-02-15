$(document).ready(function() {

    /* Dialogs */

    enableDialog($("div#add-menu-dialog"), $("a#add-menu"), 'Opprett ny menylink', '80%');
    enableDialog($("div#add-page-dialog"), $("a#add-page"), 'Opprett ny side', '80%');
    enableDialog($("div#add-album"), $("div#archive-gallery li.add.album a"), 'Legg til album', 'auto');

    /* When creating a page, slugify the title as URL */
    $("#add-page-dialog input[name='title']").keyup(function() {
        $("#add-page-dialog input[name='slug']").val(slugify($(this).val()));
    })
});

function enableDialog(dialog, button, title, width) {
    dialog.dialog({
        title: title,
        modal: true,
        autoOpen: false,
        width: width
    }).hide();
    button.click(function(event) {
        dialog.dialog('open');
    });
}

function slugify(string) {
    string = string.toLowerCase().trim();
    string = string.replace(/[^a-zæøåÆØÅ0-9-_\ ]/g, '')
    string = string.replace(/\ +/g, '-')
    return string.toLowerCase().trim();
}
