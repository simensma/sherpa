$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var position_section = editor.find("div.section.position");
    var map_element = position_section.find("div.leaflet-map");
    var popup_content = position_section.find("div.popup-content").html();
    var show_on_map = position_section.find("p.intro.show-on-map");
    var show_map = position_section.find("p.intro a.show-map");

    var counties_select = position_section.find("select[name='counties']");
    var counties_ajaxloader = position_section.find("div.control-group.counties img.ajaxloader");
    var municipalities_select = position_section.find("select[name='municipalities']");
    var municipalities_ajaxloader = position_section.find("div.control-group.municipalities img.ajaxloader");
    var locations_select = position_section.find("select[name='locations']");
    var locations_ajaxloader = position_section.find("div.control-group.locations img.ajaxloader");

    var marker;

    var initiate_map = function() {
        var map = L.map('map').setView([65, 12], 5);
        L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
            attribution: 'Kartverket'
        }).addTo(map);

        // From js_globals
        if(Turistforeningen.start_point_lat !== undefined && Turistforeningen.start_point_lng !== undefined) {
            marker = new L.Marker(new L.LatLng(Turistforeningen.start_point_lat, Turistforeningen.start_point_lng), {
                'title': 'Turen starter her'
            }).bindPopup(popup_content).addTo(map);
        }

        map.addControl(new L.Control.Draw({
            position: 'topleft',
            polyline: false,
            polygon: false,
            rectangle: false,
            circle: false,
            marker: {
                title: "Velg startposisjon"
            }
        }));

        map.on('draw:marker-created', function(e) {
            if(typeof marker !== "undefined") {
                marker.setLatLng(e.marker.getLatLng());
                marker.update();
            } else {
                e.marker.bindPopup(popup_content).addTo(map);
                marker = e.marker;
            }
            marker.openPopup();

            county_lookup(e.marker.getLatLng().lat, e.marker.getLatLng().lng);
            municipality_lookup(e.marker.getLatLng().lat, e.marker.getLatLng().lng);
            location_lookup(e.marker.getLatLng().lat, e.marker.getLatLng().lng);
        });

        map_element.find("a.leaflet-control-draw-marker").tooltip({
            placement: 'right'
        });
    };

    // Show the map
    show_map.click(function() {
        $(this).parent().remove();
        show_on_map.show();
        map_element.slideDown(initiate_map);
    });

    form.submit(function() {
        if(marker !== undefined) {
            form.find("input[name='position_lat']").val(marker.getLatLng().lat);
            form.find("input[name='position_lng']").val(marker.getLatLng().lng);
        }
    });

    function county_lookup(lat, lng) {
        counties_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-county-lookup-url'),
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
            counties_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            counties_ajaxloader.hide();
        });
    }

    function municipality_lookup(lat, lng) {
        municipalities_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-municipality-lookup-url'),
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
            municipalities_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            municipalities_ajaxloader.hide();
        });
    }

    function location_lookup(lat, lng) {
        locations_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-location-lookup-url'),
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
            locations_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            locations_ajaxloader.hide();
        });
    }

});
