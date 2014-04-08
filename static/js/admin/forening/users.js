$(function() {
    var admin = $(".foreningsadmin");
    var users = $(".foreningsadmin .useradmin");

    var initiate_access = users.find(".give-access-initiation");
    var give_access = users.find(".give-access");

    initiate_access.find("button").click(function() {
        initiate_access.hide();
        give_access.slideDown();
    });

});
