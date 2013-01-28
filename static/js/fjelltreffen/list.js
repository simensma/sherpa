$(document).ready(function() {

    var start_index;
    var loading = false;
    var complete = false;

    var wrapper = $("div.fjelltreffen-list");
    var listwrapper = $("div.annonse-list-wrapper");

    var lowerageselect = $("select.lowerage");
    var upperageselect = $("select.upperage");
    var genderselect = $("select.gender");
    var countyselect = $("select.county");

    var button_trigger = wrapper.find("button.load");
    var loader = wrapper.find("img.ajaxloader");
    var no_matches = wrapper.find("div.no-matches");
    var no_further_matches = wrapper.find("div.no-further-matches");

    lowerageselect.change(filterChanged);
    upperageselect.change(filterChanged);
    genderselect.change(filterChanged);
    countyselect.change(filterChanged);

    start_index = wrapper.attr('data-start-index');
    button_trigger.click(loadAnnonser);

    function filterChanged(){
        if(upperageselect.val() != '' && lowerageselect.val() > upperageselect.val()) {
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
            minage: lowerageselect.val(),
            maxage: upperageselect.val(),
            gender: genderselect.val(),
            //this is some jquery quirk. .val() removes leading zeroes, and focus uses leading zeroes in county codes
            county: countyselect.attr("value")
        };

        $.ajaxQueue({
            url: "/fjelltreffen/last/" + start_index + "/",
            data: {filter: JSON.stringify(filter)}
        }).done(function(result) {
            result = JSON.parse(result);
            var new_items = $(result.html).filter(function() { return this.nodeType != 3; });

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
                // Filter out text nodes
                new_items.hide();
                listwrapper.append(new_items);
                new_items.fadeIn();
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
