$(document).ready(function() {
    var register = $("div.turlederregister");
    var filters = register.find("div.search-area");
    var filters_content = filters.find("div.content");
    var filters_button = filters.find("button.search");
    var table = register.find("table.turledere");

    var turleder_search_input = filters.find("input[name='turleder']");
    var turleder_search_button = filters.find("button.turleder-search");
    var turleder_association_active = filters.find("select[name='association_active']");
    var turleder_roles = filters.find("select[name='turleder_roles']");
    var turleder_include_all_roles_label = filters.find("label.include-all-certificates");
    var turleder_include_all_roles = filters.find("input[name='include_all_certificates']");
    var turleder_association_approved = filters.find("select[name='association_approved']");

    turleder_association_approved.chosen({
        'allow_single_deselect': true
    });

    turleder_roles.chosen({
        'allow_single_deselect': true
    });

    turleder_roles.change(function() {
        if($(this).find("option:selected").val().length > 0) {
            turleder_include_all_roles_label.show();
        } else {
            turleder_include_all_roles_label.hide();
        }
    });

    var short_query = table.find("tr.short-query");

    turleder_search_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            filters_button.click();
        }
    });

    filters_button.click(function() {
        short_query.hide();
        table.find("tr.result").remove();
        var query = turleder_search_input.val();
        if(query.length !== 0 && query.length < admin_user_search_char_length) {
            short_query.show();
            return;
        }

        // Good to go
        filters_button.prop('disabled', true);
        table.data('bulk', 0);
        table.find("tr.result").remove();
        InfiniteScroller.reset();
        InfiniteScroller.trigger();
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
                query: turleder_search_input.val(),
                turleder_associations_active: JSON.stringify(get_selected_active_associations()),
                turleder_role: turleder_roles.find("option:selected").val(),
                turleder_role_include: JSON.stringify(turleder_include_all_roles.prop("checked")),
                turleder_association_approved: turleder_association_approved.find("option:selected").val()
            };
        },
        beforeLoad: function() {
            filters_button.prop('disabled', true);
        }, afterLoad: function() {
            filters_button.prop('disabled', false);
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

    function get_selected_active_associations() {
        var active = [];
        turleder_association_active.find("option:selected").each(function() {
            active.push($(this).val());
        });
        return active;
    }

});
