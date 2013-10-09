$(document).ready(function() {
    var wrapper = $("div.choose-authenticated-user");
    var form = wrapper.find("form");
    var hidden = form.find("input[type='hidden'][name='user']");
    var names = form.find("a.user-name");

    names.click(function() {
        hidden.val($(this).attr('data-user-id'));
        form.submit();
    });
});
