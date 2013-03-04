$(document).ready(function() {
    var form = $("form.edit-publication");
    var a = $("p.publication-actions a.edit-publication");

    a.click(function() {
        $(this).hide();
        form.slideDown();
    });

});
