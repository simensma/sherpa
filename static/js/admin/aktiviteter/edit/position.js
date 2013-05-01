$(document).ready(function() {
    // var map = L.map('map').setView([51.505, -0.09], 8);
    var map = L.map('map').setView([59.230596, 7.537651], 13);
    L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
        attribution: 'Kartverket'
    }).addTo(map);
});
