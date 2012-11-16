$(document).ready(function() {

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
    })

    admin_revoke_wrapper.find("a.cancel").click(function() {
        admin_buttons.show();
        admin_revoke_wrapper.hide();
    });

    var association_permission = $("div.association-permission");
    var association_select = association_permission.find("select[name='association-permission']");
    var association_revoke = $("div.association-permission-revoke");
    var association_revoke_select = association_revoke.find("select[name='association-permission-revoke']");
    var association_revoke_verify = association_revoke.find("div.association-permission-revoke-verify");
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

    association_revoke_select.chosen({
        'allow_single_deselect': true
    }).change(function() {
        var selected = association_revoke_select.find("option:selected");
        if(selected.val() == "") {
            association_revoke_verify.hide();
        } else {
            association_revoke_verify.show();
            association_revoke_verify.find("span.association").text(selected.text());
            association_revoke_verify.find("form input[name='association']").val(selected.val());
        }
    });

    association_revoke_verify.find("a.cancel").click(function() {
        association_revoke_verify.hide();
        association_revoke_select.val('');
        association_revoke_select.trigger('liszt:updated');
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

    var sherpa_user_button = $("button.make-sherpa-user");
    var sherpa_user = $("div.make-sherpa-user");

    sherpa_user_button.click(function() {
        $(this).hide();
        sherpa_user.show();
    });

    sherpa_user.find("a.cancel").click(function() {
        sherpa_user_button.show();
        sherpa_user.show();
    });
});
