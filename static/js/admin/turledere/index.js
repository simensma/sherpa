$(function() {
    var register = $("div.turlederregister");
    var filters = register.find("div.search-area");
    var filters_content = filters.find("div.content");
    var filters_button = filters.find("button.search");
    var table = register.find("table.turledere");

    var toggle_create = register.find("a.toggle-create");
    var turleder_search_input = filters.find("input[name='turleder']");
    var turleder_search_button = filters.find("button.turleder-search");
    var turleder_forening_active = filters.find("select[name='forening_active']");
    var turleder_roles = filters.find("select[name='turleder_roles']");
    var only_kursledere = filters.find('input[name="only_kursledere"]');
    var instruktor_roles = filters.find("select[name='instruktor_roles']");
    var turleder_include_all_roles_label = filters.find("label.include-all-certificates");
    var turleder_include_all_roles = filters.find("input[name='include_all_certificates']");
    var turleder_forening_approved = filters.find("select[name='forening_approved']");


    register.find("div.tab-pane").each(function() {
        var id = $(this).attr('id');
        $.fn.Hashtag('bind', id, {
            'match': function() {
                register.find("ul.nav a[href='#" + id + "']").tab('show');
            }
        });
    });

    toggle_create.click(function() {
        register.find("ul.nav a[href='#create']").tab('show');
    });

    turleder_forening_approved.chosen({
        'allow_single_deselect': true
    });

    turleder_roles.chosen({
        'allow_single_deselect': true
    });

    turleder_roles.change(function() {
        if($(this).find("option:selected").val().length > 0) {
            // Explicitly force block-display; or it would've been set to inline-block
            turleder_include_all_roles_label.show().css('display', 'block');
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
        if(query.length !== 0 && query.length < Turistforeningen.admin_user_search_char_length) {
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
                turleder_foreninger_active: JSON.stringify(get_selected_active_foreninger()),
                turleder_role: turleder_roles.find("option:selected").val(),
                only_kursledere: JSON.stringify(only_kursledere.prop('checked')),
                instruktor_roles: JSON.stringify(get_selected_instruktor_roles()),
                turleder_role_include: JSON.stringify(turleder_include_all_roles.prop("checked")),
                turleder_forening_approved: turleder_forening_approved.find("option:selected").val()
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
            },
            fail: function(result) {
                table.find('tr.technical-error').show();
            },
        }
    });
    InfiniteScroller.trigger();

    function get_selected_active_foreninger() {
        var active = [];
        turleder_forening_active.find("option:selected").each(function() {
            active.push($(this).val());
        });
        return active;
    }

    function get_selected_instruktor_roles() {
        var roles = [];
        instruktor_roles.find("option:selected").each(function() {
            roles.push($(this).val());
        });
        return roles;
    }

    // Member-search

    var member_search = register.find("div.member-search");
    var member_search_input = member_search.find("input[name='member-search']");
    var member_search_button = member_search.find("button.member-search");

    var member_search_table = member_search.find("table.member-search-list");
    var member_search_loader = member_search_table.find("tr.loader");
    var member_search_short_query = member_search_table.find("tr.short-query");
    var member_search_error = member_search_table.find("tr.technical-error");
    var member_search_no_hits = member_search_table.find("tr.no-hits");

    member_search_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            member_search_button.click();
        }
    });

    member_search_button.click(function() {
        var reset = function() {
            member_search_loader.hide();
            member_search_input.prop('disabled', false);
            member_search_button.prop('disabled', false);
        };

        member_search_table.show();

        member_search_input.prop('disabled', true);
        member_search_button.prop('disabled', true);
        member_search_table.find("tr.result").remove();
        member_search_short_query.hide();
        member_search_error.hide();
        member_search_loader.show();
        member_search_no_hits.hide();

        var query = member_search_input.val();
        if(query.length < Turistforeningen.admin_user_search_char_length) {
            member_search_short_query.show();
            reset();
            return;
        }

        $.ajaxQueue({
            url: member_search_table.attr('data-search-url'),
            data: { query: query }
        }).done(function(result) {
            member_search_table.find("tr.result").remove();
            if(result.trim() === '') {
                member_search_no_hits.show();
            } else {
                var html = $.parseHTML(result.trim());
                member_search_table.append(html);
            }
        }).fail(function(result) {
            member_search_table.find("tr.result").remove();
            member_search_error.show();
        }).always(reset);
    });

});
