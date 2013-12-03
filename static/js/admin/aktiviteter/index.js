$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var actual_listing = listing.find("div.list-wrapper");

    var association_filter_select = actual_listing.find("select[name='association_filter']");
    association_filter_select.change(function() {
        window.location = $(this).find("option:selected").attr('data-filter-url');
    });

});
