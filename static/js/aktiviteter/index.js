$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var filters = listing.find("div.search-filters");

    filters.find("select").chosen({
        'allow_single_deselect': true
    });
});
