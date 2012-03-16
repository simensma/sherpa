$(document).ready(function() {

    /* Enable all dialogs */
    $(".dialog").enableDialog();
    $(".dialog-button").enableDialogButton();

    /* When creating a page, slugify the title as URL */
    $("#add-page-dialog input[name='title']").keyup(function() {
        $("#add-page-dialog input[name='slug']").val(slugify($(this).val()));
    })
});

$.fn.enableDialog = function() {
    return this.each(function() {
        $(this).dialog({
            title: $(this).attr('data-title'),
            modal: true,
            autoOpen: false,
            width: $(this).attr('data-width')
        }).hide();
    });
}

$.fn.enableDialogButton = function() {
    return this.each(function() {
        $(this).click(function(event) {
            $($(this).attr('data-dialog')).dialog('open');
        });
    });
}

function slugify(string) {
    string = string.toLowerCase().trim();
    string = string.replace(/[^a-zæøåÆØÅ0-9-_\ ]/g, '')
    string = string.replace(/\ +/g, '-')
    return string.toLowerCase().trim();
}
