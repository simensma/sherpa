$(document).ready(function() {
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
});
