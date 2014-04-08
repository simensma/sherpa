// This is getting ridiculous, merge this with the other similar search modules

$(function() {

    var admin = $("div.foreningsadmin");
    var search = admin.find("div.give-access");

    var table = search.find("table.search-results");
    var search_input = search.find("input[name='search']");
    var search_button = search.find("button.search");

    var intro = table.find("tr.intro");
    var loader = table.find("tr.loader");
    var no_hits = table.find("tr.no-hits");
    var short_query = table.find("tr.short_query");
    var error = table.find("tr.technical-error");
    var max_hits_exceeded = table.find("tr.max-hits-exceeded");
    var result_mirror = no_hits.find("span.result-mirror");


    search_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            search_button.click();
        }
    });

    search_button.click(function() {
        search_input.prop('disabled', true);
        search_button.prop('disabled', true);
        intro.hide();
        table.slideDown();
        loader.show();
        no_hits.hide();
        short_query.hide();
        error.hide();
        max_hits_exceeded.hide();
        table.find("tr.result").remove();

        var query = search_input.val();
        if(query.length < Turistforeningen.admin_user_search_char_length) {
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
                table.find("tr.result a.pick").click(function(e) {
                    // Business logic unrelated to the search logic, but I'm IN A RUSH AS USUAL :(
                    var result_row = $(this).parents("tr.result");
                    var has_sherpa_access = JSON.parse(result_row.attr('data-has-sherpa-perm'));
                    var gender;
                    if(result_row.attr('data-gender') == 'm') {
                        gender = "ham";
                    } else {
                        gender = "henne";
                    }
                    var message;
                    if(has_sherpa_access) {
                        message = "Vil du gi " + result_row.attr('data-name') + " tilgang til " + table.attr('data-forening-name') + "?";
                    } else {
                        message = result_row.attr('data-name') + " har ikke tilgang til Sherpa i dag.\n\nVil du gi " + gender + " både tilgang til Sherpa, og til " + table.attr('data-forening-name') + "?";
                    }
                    if(!confirm(message)) {
                        e.preventDefault();
                    }
                });
            }
        }).fail(function(result) {
            table.find("tr.result").remove();
            error.show();
        }).always(function(result) {
            loader.hide();
            search_input.prop('disabled', false);
            search_button.prop('disabled', false);
        });
    });

});
