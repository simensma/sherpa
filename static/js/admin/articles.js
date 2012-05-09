$(document).ready(function() {

    /* New article dialog */

    $("div.article-dialog img[data-template]").click(function() {
        if($("div.article-dialog input[name='title']").val().length == 0) {
            alert("Du må jo skrive inn en tittel på siden før du oppretter den!");
            return;
        }
        $("div.article-dialog input[name='template']").val($(this).attr('data-template'));
        $(this).parents("form").submit();
    });

});
