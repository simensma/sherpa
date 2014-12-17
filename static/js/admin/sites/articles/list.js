$(function() {

    var table = $("table.article-listing");
    var container = table.children("tbody");
    var new_article_modal = $("div.new-article");

    $("a.new-article").click(function() {
        new_article_modal.modal({
            maskMessage: 'Oppretter nyhet...'
        });
    });

    new_article_modal.find('.template-select .template-item').click(function (e) {
        new_article_modal.find('.template-select .template-item.active.selected').removeClass('active selected');
        $(this).addClass('active selected');
    });

    new_article_modal.find('button[data-dnt-action="create-article"]').click(function() {

        if (new_article_modal.find("input[name='title']").val().length === 0) {
            alert("Du må skrive inn en tittel på artikkelen før du oppretter den!");
            return;
        }

        new_article_modal.find("input[name='template']")
            .val(new_article_modal.find('.template-select .active')
            .attr('data-template'));

        new_article_modal.find("form").submit();

        var $modal = $(this).parents('.modal').first();
        $modal.modal('mask');
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
