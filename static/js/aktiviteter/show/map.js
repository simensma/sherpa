$(document).ready(function() {
    var aktivitet = $("div.aktivitet");
    var popup_content = aktivitet.find("div.leaflet-popup-content").html();

    var map = L.map('map').setView([Turistforeningen.start_point_lat, Turistforeningen.start_point_lng], 5);
    L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
        attribution: 'Kartverket'
    }).addTo(map);

    marker = new L.Marker(new L.LatLng(Turistforeningen.start_point_lat, Turistforeningen.start_point_lng), {
        'title': 'Turen starter her'
    }).bindPopup(popup_content).addTo(map);
});
