$(document).ready(function() {
    var form = $("form.edit-publication");
    var association_select = form.find("select[name='association']");
    var access = form.find("div.control-group.access");
    var access_association_name = access.find("span.association-name");

    association_select.change(function() {
        var selected = $(this).find("option:selected");
        if(selected.attr("data-type") == "sentral") {
            access.hide();
        } else {
            access.show();
            var name = window.association_main_mappings[selected.val()];
            access_association_name.text(name);
        }
    });

});
