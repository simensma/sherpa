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
        perform_search('turledere', turleder_search_input.val());
    });

    function perform_search(search_type, query) {
        short_query.hide();
        error.hide();
        if(search_type !== 'all' && query.length < admin_user_search_char_length) {
            short_query.show();
            return;
        }
        loading.show();
        table.find("tr.result").remove();

        turleder_search_input.prop('disabled', true);
        turleder_search_button.prop('disabled', true);

        $.ajaxQueue({
            url: register.attr('data-search-url'),
            data: {
                search_type: search_type,
                query: query
            }
        }).done(function(result) {
            table.append($.parseHTML(result));
        }).fail(function() {
            error.show();
        }).always(function() {
            loading.hide();
            turleder_search_input.prop('disabled', false);
            turleder_search_button.prop('disabled', false);
        });
    }
});
