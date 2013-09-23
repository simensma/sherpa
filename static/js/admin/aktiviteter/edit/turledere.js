$(document).ready(function() {

    var editor = $("div.edit-aktivitet-turledere");

    var turleder_table = editor.find("div.date table.turledere");

    turleder_table.find("form.remove-turleder a.remove").click(function() {
        var name = $(this).parent().text().trim();
        if(confirm("Er du sikker på at du vil ta bort turleder-tilgangen fra " + name + "?")) {
            $(this).parent().submit();
        }
    });

    var search = editor.find("div.turleder-search");
    var input = search.find("input[name='turleder-search']");
    var button = search.find("button.turleder-search");
    var table = search.find("table.search-results");
    var loader = table.find("tr.loader");
    var no_hits = table.find("tr.no-hits");
    var short_query = table.find("tr.short_query");
    var error = table.find("tr.technical-error");
    var max_hits_exceeded = table.find("tr.max-hits-exceeded");
    var result_mirror = no_hits.find("span.result-mirror");

    input.keyup(function(e) {
        if(e.which == 13) { // Enter
            button.click();
        }
    });

    button.click(function() {
        input.prop('disabled', true);
        button.prop('disabled', true);
        table.show();
        loader.show();
        no_hits.hide();
        short_query.hide();
        error.hide();
        max_hits_exceeded.hide();
        table.find("tr.result").remove();

        var query = input.val();
        if(query.length < Turistforeningen.admin_user_search_char_length) {
            input.prop('disabled', false);
            button.prop('disabled', false);
            short_query.show();
            loader.hide();
            return;
        }

        $.ajaxQueue({
            url: table.attr('data-search-url'),
            data: {
                q: query,
                aktivitet: editor.attr('data-aktivitet-id')
            }
        }).done(function(result) {
            result = JSON.parse(result);
            table.find("tr.result").remove();
            if(result.results.trim() === '') {
                result_mirror.text(query);
                no_hits.show();
            } else {
                table.append(result.results);
                if(result.max_hits_exceeded) {
                    max_hits_exceeded.show();
                }
            }
        }).fail(function(result) {
            table.find("tr.result").remove();
            error.show();
        }).always(function(result) {
            loader.hide();
            input.prop('disabled', false);
            button.prop('disabled', false);
        });
    });

    $(document).on('click', table.selector + ' tr.result button.assign-turleder', function() {
        var form = $(this).siblings("form");
        if(form.find("input[name='aktivitet_dates']").length == 1) {
            // Only one date, submit it automatically
            form.find("input[name='aktivitet_dates']").prop('checked', true);
            form.submit();
        } else {
            // Multiple, let the user choose
            $(this).hide();
            form.slideDown();
        }
    });

});
