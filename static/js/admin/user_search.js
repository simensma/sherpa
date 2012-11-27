$(document).ready(function() {
    (function(AdminUserSearch, $, undefined ) {

        var search_input = $("input[name='user-search']");
        var search_button = search_input.siblings("button");
        var table = $("table.user-search-list");
        var loader = table.find("tr.loader");
        var initial = table.find("tr.initial");
        var no_hits = table.find("tr.no-hits");
        var result_mirror = no_hits.find("span.result-mirror");
        var MIN_LENGTH = 3;

        var search_id;
        var previous_query = "";
        search_input.keyup(search_soon);
        search_button.click(search_soon);

        function search_soon() {
            var query = search_input.val();
            if(query.length < MIN_LENGTH || query == previous_query) {
                return;
            }
            previous_query = query;
            loader.show();
            no_hits.hide();
            initial.hide();
            table.find("tr.result").remove();
            clearInterval(search_id);
            search_id = setTimeout(search, 1000);
        }

        function search() {
            var query = search_input.val();
            $.ajaxQueue({
                url: '/sherpa/brukere/søk/',
                data: 'q=' + encodeURIComponent(query)
            }).done(function(result) {
                if(result.trim() == '') {
                    result_mirror.text(query);
                    no_hits.show();
                } else {
                    table.append(result);
                }
            }).fail(function(result) {
            }).always(function(result) {
                loader.hide();
            });
        }

    }(window.AdminUserSearch = window.AdminUserSearch || {}, jQuery ));
});
