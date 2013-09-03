$(document).ready(function() {
    var register = $("div.turlederregister");
    var table = register.find("table.turledere");

    var turleder_search_input = register.find("input[name='turleder']");
    var turleder_search_button = register.find("button.turleder-search");
    var turleder_association = register.find("select[name='association']");

    turleder_association.chosen({
        'allow_single_deselect': true
    });

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

        setInputDisabled(true);

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
            table.append($.parseHTML(JSON.parse(result).html));
        }).fail(function() {
            error.show();
        }).always(function() {
            loading.hide();
            setInputDisabled(false);
        });
    });

    table.data('bulk', 0);
    InfiniteScroller.enable({
        url: table.attr('data-infinite-scroll-url'),
        triggerType: 'scroll',
        trigger: table,
        container: table,
        loader: register.find("div.infinite-scroll-loader"),
        ajaxData: function() {
            var bulk = Number(table.data('bulk'));
            table.data('bulk', bulk + 1);
            return {
                bulk: bulk,
                search_type: 'infinite',
                turleder_association: turleder_association.find("option:selected").val()
            };
        },
        beforeLoad: function() {
            setInputDisabled(true);
        }, afterLoad: function() {
            setInputDisabled(false);
        }, handlers: {
            done: function(result) {
                result = JSON.parse(result);
                if(result.complete) {
                    InfiniteScroller.end();
                }
                table.append($.parseHTML(result.html.trim()));
            }
        }
    });
    InfiniteScroller.trigger();

    turleder_association.change(function() {
        table.data('bulk', 0);
        table.find("tr.result").remove();
        InfiniteScroller.reset();
        InfiniteScroller.trigger();
    });

    function setInputDisabled(disabled) {
        turleder_search_input.prop('disabled', disabled);
        turleder_search_button.prop('disabled', disabled);
        turleder_association.find("option").prop('disabled', disabled);
        var tmp = turleder_association.attr('data-placeholder-wait');
        turleder_association.attr('data-placeholder-wait', turleder_association.attr('data-placeholder'));
        turleder_association.attr('data-placeholder', tmp);
        turleder_association.trigger('liszt:updated');
    }

});
