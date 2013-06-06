$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var filters = listing.find("div.search-filters");
    var popups = listing.find("div.popups");

    filters.find("select").chosen({
        'allow_single_deselect': true
    });

    var map = L.map('map').setView([65, 12], 5);
    L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
        attribution: 'Kartverket'
    }).addTo(map);

    var p = Turistforeningen.aktivitet_points;
    for(var i=0; i<p.length; i++) {
        var popup_content = popups.find("div[data-aktivitet-date-id='" + p[i].id + "']");
        marker = new L.Marker(new L.LatLng(p[i].lat, p[i].lng), {
            'title': popup_content.find("h3").text()
        }).bindPopup(popup_content.html()).addTo(map);
    }
});
