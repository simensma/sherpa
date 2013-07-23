$(document).ready(function() {

    var wrapper = $("div.edit-aktivitet-position");
    var map_element = wrapper.find("div.leaflet-map");
    var popup_content = wrapper.find("div.popup-content").html();
    var form = wrapper.find("form.save-position");

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

    form.submit(function(e) {
        if(marker === undefined) {
            alert("Du må velge en posisjon å lagre først. Klikk på ikonet oppe i venstre hjørne av kartet, og klikk der turen starter.");
            e.preventDefault();
            return $(this);
        }
        form.find("input[name='lat']").val(marker.getLatLng().lat);
        form.find("input[name='lng']").val(marker.getLatLng().lng);
    });

});
