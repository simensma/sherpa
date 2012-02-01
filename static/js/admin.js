$(document).ready(function() {

    /* Dialogs */

    $("div#add-menu-dialog").dialog({
        title: 'Opprett ny meny',
        modal: true,
        autoOpen: false,
        width: "80%"
    }).hide();
    $("a#add-menu").click(function(event) {
        $("div#add-menu-dialog").dialog('open');
    });

    $("div#add-page-dialog").dialog({
        title: 'Opprett ny side',
        modal: true,
        autoOpen: false,
        width: "80%"
    }).hide();
    $("a#add-page").click(function(event) {
        $("div#add-page-dialog").dialog('open');
    });

    $("div#add-album").dialog({
        title: 'Legg til album',
        modal: true,
        autoOpen: false,
        width: "80%"
    }).hide();
    $("div#archive-gallery li.add.album a").click(function(event) {
        $("div#add-album").dialog('open');
    });

    $("div#archive-gallery li.add.image a").click(function(event) {
        // add image
    });

    /* When creating a page, slugify the title as URL */
    $("#add-page-dialog input[name='title']").keyup(function() {
        $("#add-page-dialog input[name='slug']").val(slugify($(this).val()));
    })
});

function slugify(string) {
    string = string.toLowerCase().trim();
    string = string.replace(/[^a-zæøåÆØÅ0-9-_\ ]/g, '')
    string = string.replace(/\ +/g, '-')
    return string.toLowerCase().trim();
}
