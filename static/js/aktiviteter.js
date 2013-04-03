$(document).ready(function() {
    var filters = $("div.aktivitet-search-filters");

    filters.find("select").chosen({
        'allow_single_deselect': true
    });
});
