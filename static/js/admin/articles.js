$(document).ready(function() {

    var table = $("table.article-listing");

    $("a.new-article").click(function() {
        $("div.new-article").modal();
    });

    $("div.new-article img[data-template]").click(function() {
        if($("div.new-article input[name='title']").val().length === 0) {
            alert("Du må skrive inn en tittel på artikkelen før du oppretter den!");
            return;
        }
        $("div.new-article input[name='template']").val($(this).attr('data-template'));
        $(this).parents("form").submit();
    });

    InfiniteScroller.enable({
        container: table.children("tbody"),
        loader: $("div.infinite-scroll-loader")
    });

});
