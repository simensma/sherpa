$(document).ready(function() {

    var button = $("button.create-publication");
    var form = $("form.edit-publication");

    button.click(function() {
        $(this).hide();
        form.slideDown();
    });

});
