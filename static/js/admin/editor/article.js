/* Specific article-editing scripts */

$(document).ready(function() {
    $("div[data-type='title']").focusout(function() {
        $("a.header-title").text($(this).text());
    });
});
