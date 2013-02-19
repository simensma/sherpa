$(document).ready(function() {
    var wrapper = $("div.choose-authenticated-user");
    var form = wrapper.find("form");
    var hidden = form.find("input[type='hidden'][name='profile']");
    var names = form.find("a.profile-name");

    names.click(function() {
        hidden.val($(this).attr('data-profile-id'));
        form.submit();
    });
});
