$(function() {
    var edit_domain = $("a.edit-domain");
    var domain_modal = $("div.modal.domain");
    edit_domain.click(function() {
        domain_modal.modal();
    });
});
