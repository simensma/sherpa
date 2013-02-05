$(document).ready(function() {

    var start_index;
    var loading = false;
    var complete = false;

    var wrapper = $("div.fjelltreffen-list");
    var listwrapper = wrapper.find("table.list-public");

    var input_min_age = $("select[name='min_age']");
    var input_max_age = $("select[name='max_age']");
    var input_gender = $("select[name='gender']");
    var input_county = $("select[name='county']");
    var input_text = $("input[name='text']");

    var button_trigger = wrapper.find("button.load");
    var loader = wrapper.find("img.ajaxloader");
    var no_matches = wrapper.find("div.no-matches");
    var no_further_matches = wrapper.find("div.no-further-matches");

    input_min_age.change(filterChanged);
    input_max_age.change(filterChanged);
    input_gender.change(filterChanged);
    input_county.change(filterChanged);
    input_text.keyup(function() {
        clearTimeout(text_trigger_timeout_id);
        text_trigger_timeout_id = setTimeout(filterChanged, text_trigger_timeout);
    });
    var text_trigger_timeout_id;
    var text_trigger_timeout = 800; // Milliseconds

    start_index = wrapper.attr('data-start-index');
    button_trigger.click(loadAnnonser);

    function filterChanged(){
        if(input_max_age.val() != '' && input_min_age.val() > input_max_age.val()) {
            alert("Du kan ikke søke fra en høyere alder til en lavere alder! Det får du ingen treff på. Velg en annen aldersgruppe.");
            return;
        }

        start_index = 0;
        complete = false;

        no_matches.fadeOut();
        no_further_matches.fadeOut();

        listwrapper.fadeOut(function() {
            $(this).empty().show();
            loadAnnonser();
        });
    }

    function loadAnnonser(){
        loading = true;
        button_trigger.hide();
        loader.show();

        var filter = {
            minage: input_min_age.val(),
            maxage: input_max_age.val(),
            gender: input_gender.val(),
            //this is some jquery quirk. .val() removes leading zeroes, and focus uses leading zeroes in county codes
            county: input_county.attr("value"),
            text: input_text.val()
        };

        $.ajaxQueue({
            url: "/fjelltreffen/last/" + start_index + "/",
            data: {filter: JSON.stringify(filter)}
        }).done(function(result) {
            result = JSON.parse(result);
            var new_items = $(result.html).filter(function() { return this.nodeType != 3; }); // Filter out text nodes

            if(new_items.length == 0) {
                // No results
                if(start_index == 0) {
                    // This was a new filter with no matches
                    no_matches.fadeIn();
                } else {
                    no_further_matches.fadeIn();
                }
                complete = true;
            } else {
                // Hide/show the cell elements - fade won't work on table rows
                new_items.find("td").hide();
                listwrapper.append(new_items);
                new_items.find("td").fadeIn();
                if(!result.end) {
                    button_trigger.show();
                } else {
                    no_further_matches.fadeIn();
                }
            }
            start_index = result.start_index;
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere annonser. Prøv å oppdatere siden, og scrolle ned igjen.");
        }).always(function(result) {
            loading = false;
            loader.hide();
        });
    }
});
