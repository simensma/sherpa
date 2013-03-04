$(document).ready(function() {
    var delete_anchor = $("a.delete-release");
    var delete_confirm = $("div.delete-release-confirm");
    var delete_final = $("a.delete-release-final");

    delete_anchor.click(function() {
        $(this).hide();
        delete_confirm.show();
    });

    delete_final.click(function(e) {
        if(!confirm("Siste sjanse til å avbryte - sikker på at du vil slette utgivelsen?")) {
            e.preventDefault();
        }
    });
});
