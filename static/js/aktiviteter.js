$(document).ready(function() {
    var filters = $("div.aktivitet-search-filters");

    filters.find("select").chosen({
        'allow_single_deselect': true
    });

    filters.find("a.toggle-search-filters").click(function() {
        $(this).parent().empty().text($(this).text());
        filters.find("div.filters").slideDown();
    });
});
