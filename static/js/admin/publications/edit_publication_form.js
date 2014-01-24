$(document).ready(function() {
    var form = $("form.edit-publication");
    var forening_select = form.find("select[name='forening']");
    var access = form.find("div.form-group.access");
    var access_forening_name = access.find("span.forening-name");

    forening_select.change(function() {
        var selected = $(this).find("option:selected");
        if(selected.attr("data-type") == "sentral") {
            access.hide();
        } else {
            access.show();
            var name = Turistforeningen.forening_main_mappings[selected.val()];
            access_forening_name.text(name);
        }
    });

});
