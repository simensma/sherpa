$(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var position_section = editor.find("div.section.position");
    var map_container = position_section.find("div.map-container");
    var show_map_button = position_section.find("a.show-map");

    var counties_select = position_section.find("select[name='counties']");
    var counties_ajaxloader = counties_select.nextAll("img.ajaxloader");
    var municipalities_select = position_section.find("select[name='municipalities']");
    var municipalities_ajaxloader = municipalities_select.nextAll("img.ajaxloader");
    var locations_select = position_section.find("select[name='locations']");
    var locations_ajaxloader = locations_select.nextAll("img.ajaxloader");

    var marker, map;

    function sted_to_html(sted) {
        return [
            '<label>' + sted.text + '</label><br>',
            '<small>' + [sted.navnetype, sted.kommunenavn, sted.fylkesnavn].join(' i ') + '</small>'
        ].join('');
    };

    function init_map(opts) {
        if (map) { return; }

        var tile_url = [
            'http://opencache.statkart.no/gatekeeper/gk/',
            'gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}'
        ].join('');

        map = L.map('map', {
            dragging: false,
            zoomControl: false,
            scrollWheelZoom: false,
            closePopupOnClick: false,
            layers: [L.tileLayer(tile_url, {attribution: 'Kartverket'})]
        });

        if (opts && opts.set_default_view) { map.setView([65, 12], 5); }
    };

    function set_map_marker(sted) {
        if (!map || (marker && marker.ssr_id === sted.id)) { return; }

        //lat = lat || Turistforeningen.start_point_lat;
        //lon = lon || Turistforeningen.start_point_lng;

        if (sted.nord && sted.aust) {
            var latlng = new L.LatLng(sted.nord, sted.aust);

            if (marker) {
                marker.setLatLng(latlng);
            } else {
                marker = L.marker(latlng, {title: 'Turern starter her'}).addTo(map);
            }

            marker.ssr_id = sted.id
            marker.bindPopup(sted_to_html(sted), { closeButton: false });
            map.setView(latlng, 12, {reset: true});
            marker.openPopup()

            form.find("input[name='position_lat']").val(marker.getLatLng().lat);
            form.find("input[name='position_lng']").val(marker.getLatLng().lng);
        }
    };

    function show_and_set_map_marker(sted) {
        map_container.show(function() {
            init_map({set_default_view: false});
            set_map_marker(sted);
            init_metadata(sted);

            var map_top = $(map_container).offset().top;
            $('html, body').animate({scrollTop:(map_top - 80)}, '500', 'swing');
        });
    };

    function location_select() {
        var select;

        select = $('[data-container="location-select"] input').select2({
            placeholder: 'Hvor starter turen?',
            minimumInputLength: 2,
            escapeMarkup: function (m) { return m; },
            formatSearching: function () { return 'Søker'; },
            formatInputTooShort: function (term, minLength) { return 'Minimum to bokstaver'; },
            formatResult: sted_to_html,
            query: location_select_query
        });

        select.on('change', function(e) {
            if (e.added) { show_and_set_map_marker(e.added); }
        });

        select.select2('open');
    };

    function location_select_query(options) {
        var res = []
          , ssr = $.fn.SSR(options.term);

        ssr.done(function(steder) {
            if (steder.stedsnavn && steder.stedsnavn.length > 0) {
                for (var i = 0; i < steder.stedsnavn.length; i++) {
                    steder.stedsnavn[i].id = steder.stedsnavn[i].ssrId;
                    steder.stedsnavn[i].text = steder.stedsnavn[i].stedsnavn;
                }

                res = steder.stedsnavn;
            }
        });

        ssr.always(function() {
            options.callback({results: res});
        });
    };

    function turforslag_select() {

    };

    function update_metadata_placeholder(e) {
        var html = $.map($(e.target).find('option:selected'), function(option) {
            return $(option).html().trim();
        }).join(', ');
        $(this).html(html || 'Ingen funnet');
    }

    function init_metadata(sted) {
        var placeholder = position_section.find('[data-placeholder-for="municipality"]');
        municipalities_select.on("chosen:updated", update_metadata_placeholder.bind(placeholder));

        var placeholder = position_section.find('[data-placeholder-for="county"]');
        counties_select.on("chosen:updated", update_metadata_placeholder.bind(placeholder));

        var placeholder = position_section.find('[data-placeholder-for="location"]');
        locations_select.on("chosen:updated", update_metadata_placeholder.bind(placeholder));

        // Look up conties, municipalities, and location based on sted
        county_lookup(sted.nord, sted.aust);
        municipality_lookup(sted.nord, sted.aust);
        location_lookup(sted.nord, sted.aust);

        position_section.find('[data-container="metadata-select"]').removeClass('jq-hide');
    };

    function county_lookup(lat, lng) {
        var url = position_section.find('[data-county-lookup-url]').data('countyLookupUrl');

        counties_ajaxloader.show();
        $.ajaxQueue({
            url: url,
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            counties_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                counties_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            counties_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            counties_ajaxloader.hide();
        });
    }

    function municipality_lookup(lat, lng) {
        var url = position_section.find('[data-municipality-lookup-url]').data('municipalityLookupUrl');

        municipalities_ajaxloader.show();
        $.ajaxQueue({
            url: url,
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            municipalities_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                municipalities_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            municipalities_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            municipalities_ajaxloader.hide();
        });
    }

    function location_lookup(lat, lng) {
        var url = position_section.find('[data-location-lookup-url]').data('locationLookupUrl');

        locations_ajaxloader.show();
        $.ajaxQueue({
            url: url,
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            locations_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                locations_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            locations_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            locations_ajaxloader.hide();
        });
    }

    $(document).on('click', '[data-show="location-select"]', function (e) {
        e.preventDefault();
        position_section.find('[data-container="location-select"]').removeClass('jq-hide');
        location_select();
    });

    $(document).on('click', '[data-show="turforslag-select"]', function (e) {
        e.preventDefault();
        position_section.find('[data-container="turforslag-select"]').removeClass('jq-hide');
        turforslag_select();
    });

    // DEMO: Simple toggling of fields, for demo purposes only
    $(document).on('click', '[data-toggle="counties-edit-show"]', function (e) {
        e.preventDefault();
        position_section.find('.counties-static').addClass('jq-hide');
        position_section.find('.counties-edit').removeClass('jq-hide');
    });

    $(document).on('click', '[data-toggle="municipalities-edit-show"]', function (e) {
        e.preventDefault();
        position_section.find('.municipalities-static').addClass('jq-hide');
        position_section.find('.municipalities-edit').removeClass('jq-hide');
    });

    $(document).on('click', '[data-toggle="locations-edit-show"]', function () {
        position_section.find('.locations-static').addClass('jq-hide');
        position_section.find('.locations-edit').removeClass('jq-hide');
    });
});
