$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var actual_listing = listing.find("div.list-wrapper");

    var forening_filter_select = actual_listing.find("select[name='forening_filter']");
    forening_filter_select.change(function() {
        window.location = $(this).find("option:selected").attr('data-filter-url');
    });

});
