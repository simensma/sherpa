$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var position_section = editor.find("div.section.position");
    var map_element = position_section.find("div.leaflet-map");
    var popup_content = position_section.find("div.popup-content").html();

    var map = L.map('map').setView([65, 12], 5);
    L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
        attribution: 'Kartverket'
    }).addTo(map);
    var marker;

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
    });

    map_element.find("a.leaflet-control-draw-marker").tooltip({
        placement: 'right'
    });

    form.submit(function() {
        if(marker !== undefined) {
            form.find("input[name='position_lat']").val(marker.getLatLng().lat);
            form.find("input[name='position_lng']").val(marker.getLatLng().lng);
        }
    });

});
