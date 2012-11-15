$(document).ready(function() {
    var admin_anchor = $("a.make-sherpa-admin");
    var admin_wrapper = $("div.make-sherpa-admin");
    admin_anchor.click(function() {
        $(this).hide();
        admin_wrapper.show();
    });

    admin_wrapper.find("a.cancel").click(function() {
        admin_anchor.show();
        admin_wrapper.hide();
    });

    var association_permission = $("div.association-permission");
    var association_select = association_permission.find("select[name='association-permission']");
    var association_role = $("div.association-role");
    var user_role_button = association_role.find("button.user");
    var admin_role_button = association_role.find("button.admin");
    var verifier = $("div.verify-association-permission");

    association_select.chosen().change(function() {
        association_role.show();
        var selected = association_select.find("option:selected");
        if(selected.attr('data-role') == 'admin') {
            association_role.find("div.admin").show();
        } else if(selected.attr('data-role') == 'user') {
            association_role.find("div.admin").hide();
        }
    });

    var role;
    user_role_button.click(function() {  role = 'user'; verifyRole('brukertilgang'); });
    admin_role_button.click(function() { role = 'admin'; verifyRole('administratortilgang'); });

    function verifyRole(role) {
        association_permission.hide();
        association_role.hide();
        verifier.show();
        verifier.find("span.role").text(role);
        verifier.find("span.association").text(association_select.find("option:selected").text());
    }

    verifier.find("a.cancel").click(function() {
        association_permission.show();
        association_role.show();
        verifier.hide();
    });

    verifier.find("form").submit(function() {
        $(this).find("input[name='association']").val(association_select.find("option:selected").val());
        $(this).find("input[name='role']").val(role);
    });
});
