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
});
