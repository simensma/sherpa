$(function() {
    var admin = $(".foreningsadmin");
    var users = $(".foreningsadmin .useradmin");

    var initiate_access = users.find(".give-access-initiation");
    var give_access = users.find(".give-access");

    initiate_access.find("button").click(function() {
        initiate_access.hide();
        give_access.slideDown();
    });

    $(document).on('click', '.foreningsadmin form.give-access button.pick', function() {
        var form = $(this).parents("form");
        var wanted_role = form.find("input[name='wanted_role']");
        wanted_role.val($(this).attr('data-wanted-role'));
    });

});
