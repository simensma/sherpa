$(document).ready(function() {

    var table = $("table.article-listing");
    var container = table.children("tbody");

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

    container.data('bulk', 1);
    InfiniteScroller.enable({
        url: container.attr('data-infinite-scroll-url'),
        triggerType: 'scroll',
        trigger: container,
        container: container,
        loader: $("div.infinite-scroll-loader"),
        ajaxData: function() {
            var bulk = Number(container.data('bulk'));
            container.data('bulk', bulk + 1);
            return {
                bulk: bulk
            };
        }
    });

});
