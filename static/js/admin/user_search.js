$(document).ready(function() {
    (function(AdminUserSearch, $, undefined ) {

        var search_input = $("input[name='user-search']");
        var search_button = search_input.siblings("button");
        var table = $("table.user-search-list");
        var loader = table.find("tr.loader");
        var initial = table.find("tr.initial");
        var no_hits = table.find("tr.no-hits");
        var short_query = table.find("tr.short_query");
        var error = table.find("tr.error");
        var result_mirror = no_hits.find("span.result-mirror");

        search_input.keyup(function(e) {
            if(e.which == 13) { // Enter
                search();
            }
        });
        search_button.click(search);

        function search() {
            search_input.prop('disabled', true);
            search_button.prop('disabled', true);
            loader.show();
            no_hits.hide();
            initial.hide();
            short_query.hide();
            error.hide();
            table.find("tr.result").remove();
            var query = search_input.val();
            if(query.length < admin_user_search_char_length) {
                search_input.prop('disabled', false);
                search_button.prop('disabled', false);
                short_query.show();
                loader.hide();
                return;
            }
            $.ajaxQueue({
                url: table.attr('data-search-url'),
                data: { q: query }
            }).done(function(result) {
                table.find("tr.result").remove();
                if(result.trim() === '') {
                    result_mirror.text(query);
                    no_hits.show();
                } else {
                    table.append(result);
                }
            }).fail(function(result) {
                table.find("tr.result").remove();
                error.show();
            }).always(function(result) {
                loader.hide();
                search_input.prop('disabled', false);
                search_button.prop('disabled', false);
            });
        }

    }(window.AdminUserSearch = window.AdminUserSearch || {}, jQuery ));
});
