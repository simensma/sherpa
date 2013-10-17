$(document).ready(function() {
    var language_container = $("div.language-container");
    var form = language_container.find("form.set-language");
    var input = form.find("input[name='language']");

    language_container.find("a.language").click(function() {
        input.val($(this).attr('data-language-code'));
        form.submit();
    });
});
