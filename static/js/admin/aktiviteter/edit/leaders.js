$(document).ready(function() {

    var editor = $("div.edit-aktivitet-leaders");

    var leader = editor.find("div.control-group.leader");
    var leader_search_input = editor.find("input[name='leader-search']");
    var leader_search_button = leader_search_input.siblings("button.leader-search");
    var leader_table = $("table.leader-search-list");
    var leader_loader = leader_table.find("tr.loader");
    var leader_no_hits = leader_table.find("tr.no-hits");
    var leader_short_query = leader_table.find("tr.short_query");
    var leader_error = leader_table.find("tr.technical-error");
    var leader_max_hits_exceeded = leader_table.find("tr.max-hits-exceeded");
    var leader_result_mirror = leader_no_hits.find("span.result-mirror");

    leader_search_input.keyup(function(e) {
        if(e.which == 13) { // Enter
            leaderSearch();
        }
    });
    leader_search_button.click(leaderSearch);

    function leaderSearch() {
        leader_search_input.prop('disabled', true);
        leader_search_button.prop('disabled', true);
        leader_table.show();
        leader_loader.show();
        leader_no_hits.hide();
        leader_short_query.hide();
        leader_error.hide();
        leader_max_hits_exceeded.hide();
        leader_table.find("tr.result").remove();
        var query = leader_search_input.val();
        if(query.length < admin_user_search_char_length) {
            leader_search_input.prop('disabled', false);
            leader_search_button.prop('disabled', false);
            leader_short_query.show();
            leader_loader.hide();
            return;
        }
        $.ajaxQueue({
            url: leader.attr('data-search-url'),
            data: { q: query }
        }).done(function(result) {
            result = JSON.parse(result);
            leader_table.find("tr.result").remove();
            if(result.results.trim() === '') {
                leader_result_mirror.text(query);
                leader_no_hits.show();
            } else {
                leader_table.append(result.results);
                if(result.max_hits_exceeded) {
                    leader_max_hits_exceeded.show();
                }
            }
        }).fail(function(result) {
            leader_table.find("tr.result").remove();
            leader_error.show();
        }).always(function(result) {
            leader_loader.hide();
            leader_search_input.prop('disabled', false);
            leader_search_button.prop('disabled', false);
        });
    }

    // Found leader, choose date for leader status

    var leader_choose_date = leader.find("div.choose-date");
    var leader_choose_date_loader = leader.find("div.choose-date-loader");
    $(document).on('click', editor.selector + " div.control-group.leader a.assign-leader-status", function() {
        leader_table.hide();
        leader_choose_date_loader.show();
        var profile_id = $(this).parents("tr.result").attr("data-profile-id");
        var profile_name = $(this).parents("tr.result").attr("data-profile-name");
        $.ajaxQueue({
            url: leader_table.attr("data-add-auto-url"),
            data: {
                aktivitet: editor.attr("data-aktivitet-id"),
                profile: profile_id
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.status == 'saved') {
                // TODO: display results in a table
                alert("The leader was saved.");
            } else if(result.status == 'none') {
                alert("Det finnes ingen turdatoer for denne aktiviteten. Du må opprette turdatoene først slik at du kan velge hvilke datoer turlederen er turleder for.");
            } else if(result.status == 'multiple') {
                chooseDateForLeader(profile_id, profile_name, result.date_options);
            }
        }).fail(function() {
            alert("Beklager - det oppstod en feil når vi skulle lagre turlederstatus!\n\n" +
                "Har du sjekket at du ikke har mistet tilgang til internett?\n\n" +
                "Du kan prøve igjen så mange ganger du vil. Feilen har blitt logget i våre systemer, og hvis vi ser at det er et teknisk problem i Sherpa så skal vi rette den så snart som mulig.");
            leader_table.show();
        }).always(function() {
            leader_choose_date_loader.hide();
        });
    });

    function chooseDateForLeader(profile_id, profile_name, date_options) {
        leader_choose_date.attr("data-profile-id", profile_id);
        leader_choose_date.find("span.name").text(profile_name);
        leader_choose_date.find("div.date-options").empty().append(date_options);
        leader_choose_date.slideDown();
    }

    $(document).on('click', editor.selector + " div.control-group.leader div.choose-date div.date-options button.choose-date", function() {
        var date = $(this).attr("data-date-id");
        $.ajaxQueue({
            url: leader_choose_date.attr("data-add-manual-url"),
            data: {
                date: date,
                profile: leader_choose_date.attr("data-profile-id")
            }
        }).done(function(result) {
            // TODO: display results in a table
            alert("The leader was saved.");
            leader_choose_date.hide();
        }).fail(function() {
            alert("Beklager - det oppstod en feil når vi skulle lagre turlederstatus!\n\n" +
                "Har du sjekket at du ikke har mistet tilgang til internett?\n\n" +
                "Du kan prøve igjen så mange ganger du vil. Feilen har blitt logget i våre systemer, og hvis vi ser at det er et teknisk problem i Sherpa så skal vi rette den så snart som mulig.");
        }).always(function() {
            leader_choose_date_loader.hide();
        });
    });

});
