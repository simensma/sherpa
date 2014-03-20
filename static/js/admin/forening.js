$(function() {
    var admin = $("div.foreningsadmin");
    var form = admin.find("form.edit-forening");

    var type_input = form.find("select[name='type']");
    var group_type = form.find("div.group_type");

    var zipcode = form.find("input[name='zipcode']");
    var area = form.find("input[name='area']");
    var loader = form.find("img.ajaxloader.zipcode");

    type_input.change(function() {
        if($(this).val() == 'turgruppe') {
            group_type.show();
        } else {
            group_type.hide();
        }
    });

    zipcode.keyup(function() {
        if($(this).val().length === 4) {
            loader.show();
            LookupZipcode($(this).val(), function(result) {
                if(result.success) {
                    area.val(result.area);
                } else if(result.error == 'does_not_exist') {
                    area.val('Ukjent postnummer');
                } else if(result.error == 'technical_failure') {
                    area.val('Teknisk feil');
                }
                loader.hide();
            });
        } else {
            area.val('');
        }
    });
});
