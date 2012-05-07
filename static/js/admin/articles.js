$(document).ready(function() {

    /* New article dialog */

    $("div.article-dialog img[data-template]").click(function() {
        $("div.article-dialog input[name='template']").val($(this).attr('data-template'));
        $(this).parents("form").submit();
    });

});
