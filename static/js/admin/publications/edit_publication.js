$(document).ready(function() {
    var edit_publication_form = $("form.edit-publication");
    var edit_release_form = $("form.edit-release");
    var publication_anchor = $("p.publication-actions a.edit-publication");
    var release_anchor = $("p.publication-actions a.create-release");
    var initial_publication_info = $("p.initial-publication-info");
    var delete_anchor = $("p.publication-actions a.delete-publication");
    var delete_confirm = $("div.delete-publication-confirm");
    var delete_final = $("a.delete-publication-final");

    publication_anchor.click(function() {
        $(this).hide();
        edit_publication_form.slideDown();
    });

    release_anchor.click(create_release);
    initial_publication_info.find("a").click(create_release);

    function create_release() {
        release_anchor.hide();
        initial_publication_info.hide();
        edit_release_form.slideDown();
    }

    delete_anchor.click(function() {
        $(this).hide();
        delete_confirm.slideDown();
    });

    delete_final.click(function(e) {
        if(!confirm("Siste sjanse til å avbryte - sikker på at du vil slette HELE publikasjonen og alle utgivelsene?")) {
            e.preventDefault();
        }
    });

});
