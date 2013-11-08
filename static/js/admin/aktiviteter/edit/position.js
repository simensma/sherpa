$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var position_section = editor.find("div.section.position");
    var map_element = position_section.find("div.leaflet-map");
    var popup_content = position_section.find("div.popup-content").html();
    var show_on_map = position_section.find("p.intro.show-on-map");
    var show_map = position_section.find("p.intro a.show-map");

    var county_select = position_section.find("select[name='county']");
    var county_ajaxloader = position_section.find("div.control-group.county img.ajaxloader");
    var municipality_select = position_section.find("select[name='municipality']");
    var municipality_ajaxloader = position_section.find("div.control-group.municipality img.ajaxloader");
    var location_select = position_section.find("select[name='location']");
    var location_ajaxloader = position_section.find("div.control-group.location img.ajaxloader");

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
        county_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-county-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length === 0) {
                // TODO
                return;
            } else if(result.length > 1) {
                // TODO
            }
            county_select.find("option[value='" + result[0] + "']").prop('selected', true);
            county_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            county_ajaxloader.hide();
        });
    }

    function municipality_lookup(lat, lng) {
        municipality_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-municipality-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length === 0) {
                // TODO
                return;
            } else if(result.length > 1) {
                // TODO
            }
            municipality_select.find("option[value='" + result[0] + "']").prop('selected', true);
            municipality_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            municipality_ajaxloader.hide();
        });
    }

    function location_lookup(lat, lng) {
        location_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-location-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.length === 0) {
                // TODO
                return;
            } else if(result.length > 1) {
                // TODO
            }
            location_select.find("option[value='" + result[0] + "']").prop('selected', true);
            location_select.trigger("liszt:updated"); // Update chosen
        }).fail(function() {
            // TODO
        }).always(function() {
            location_ajaxloader.hide();
        });
    }

});
