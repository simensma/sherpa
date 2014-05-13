$(function() {

    var admin_buttons = $("p.admin-buttons");
    var admin_button = admin_buttons.find("button.make-sherpa-admin");
    var revoke_sherpa_button = admin_buttons.find("button.revoke-sherpa-access");
    var admin_wrapper = $("div.make-sherpa-admin");
    var admin_revoke_wrapper = $("div.revoke-sherpa-access");
    admin_button.click(function() {
        admin_buttons.hide();
        admin_wrapper.show();
    });

    admin_wrapper.find("a.cancel").click(function() {
        admin_buttons.show();
        admin_wrapper.hide();
    });

    revoke_sherpa_button.click(function() {
        admin_buttons.hide();
        admin_revoke_wrapper.show();
    });

    admin_revoke_wrapper.find("a.cancel").click(function() {
        admin_buttons.show();
        admin_revoke_wrapper.hide();
    });

    var forening_permission = $("div.forening-permission");
    var forening_select = forening_permission.find("select[name='forening-permission']");
    var forening_revoke = $("div.forening-permission-revoke");
    var forening_revoke_select = forening_revoke.find("select[name='forening-permission-revoke']");
    var forening_revoke_verify = forening_revoke.find("div.forening-permission-revoke-verify");
    var forening_role = $("div.forening-role");
    var user_role_button = forening_role.find("button.user");
    var admin_role_button = forening_role.find("button.admin");
    var verifier = $("div.verify-forening-permission");

    forening_select.chosen().change(function() {
        forening_role.show();
        var selected = forening_select.find("option:selected");
        if(selected.attr('data-role') == 'admin') {
            forening_role.find("div.admin").show();
        } else if(selected.attr('data-role') == 'user') {
            forening_role.find("div.admin").hide();
        }
    });

    forening_revoke_select.chosen({
        'allow_single_deselect': true
    }).change(function() {
        var selected = forening_revoke_select.find("option:selected");
        if(selected.val() === "") {
            forening_revoke_verify.hide();
        } else {
            forening_revoke_verify.show();
            forening_revoke_verify.find("span.forening").text(selected.text());
            forening_revoke_verify.find("form input[name='forening']").val(selected.val());
        }
    });

    forening_revoke_verify.find("a.cancel").click(function() {
        forening_revoke_verify.hide();
        forening_revoke_select.val('');
        forening_revoke_select.trigger('liszt:updated');
    });

    var role;
    user_role_button.click(function() {  role = 'user'; verifyRole('brukertilgang'); });
    admin_role_button.click(function() { role = 'admin'; verifyRole('administratortilgang'); });

    function verifyRole(role) {
        forening_permission.hide();
        forening_role.hide();
        verifier.show();
        verifier.find("span.role").text(role);
        verifier.find("span.forening").text(forening_select.find("option:selected").text());
    }

    verifier.find("a.cancel").click(function() {
        forening_permission.show();
        forening_role.show();
        verifier.hide();
    });

    verifier.find("form").submit(function() {
        $(this).find("input[name='forening']").val(forening_select.find("option:selected").val());
        $(this).find("input[name='role']").val(role);
    });

    var sherpa_user_button = $("button.make-sherpa-user");
    var sherpa_user = $("div.make-sherpa-user");

    sherpa_user_button.click(function() {
        $(this).hide();
        sherpa_user.show();
    });

    sherpa_user.find("a.cancel").click(function() {
        sherpa_user_button.show();
        sherpa_user.hide();
    });


});
