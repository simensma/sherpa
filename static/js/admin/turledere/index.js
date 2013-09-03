$(document).ready(function() {
    var register = $("div.turlederregister");
    var table = register.find("table.turledere");

    var turleder_search_input = register.find("input[name='turleder']");
    var turleder_search_button = register.find("button.turleder-search");

    var short_query = table.find("tr.short-query");
    var loading = table.find("tr.loading");
    var error = table.find("tr.technical-error");

    turleder_search_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            turleder_search_button.click();
        }
    });

    turleder_search_button.click(function() {
        table.find("tr.result").remove();
        var query = turleder_search_input.val();
        short_query.hide();
        error.hide();
        if(query.length < admin_user_search_char_length) {
            short_query.show();
            return;
        }
        loading.show();

        turleder_search_input.prop('disabled', true);
        turleder_search_button.prop('disabled', true);

        $.ajaxQueue({
            url: register.attr('data-search-url'),
            data: {
                search_type: 'query',
                query: query
            }
        }).done(function(result) {
            // Remove again, because the infinite scroller may have added results after the call
            // was initiated.
            table.find("tr.result").remove();
            table.append($.parseHTML(result));
        }).fail(function() {
            error.show();
        }).always(function() {
            loading.hide();
            turleder_search_input.prop('disabled', false);
            turleder_search_button.prop('disabled', false);
        });
    });

    table.data('bulk', 0);
    InfiniteScroller.enable({
        url: table.attr('data-infinite-scroll-url'),
        triggerType: 'scroll',
        trigger: table,
        container: table,
        loader: $("div.infinite-scroll-loader"),
        ajaxData: function() {
            var bulk = Number(table.data('bulk'));
            table.data('bulk', bulk + 1);
            return {
                bulk: bulk,
                search_type: 'infinite',
            };
        }
    });
    InfiniteScroller.trigger();

});
