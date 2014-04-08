$(document).ready(function() {

    var results = $("table#results");

    /* Toggle maps */
    $(document).on('click', results.selector + ' a.open-map', function() {
        var id = $(this).attr('data-id');
        $(this).hide();
        results.find("a.close-map[data-id='" + id + "']").show();
        results.find("div.map[data-id='" + id + "']").show();
        // Actually load the iframe
        var iframe = results.find("div.map[data-id='" + id + "'] iframe");
        if(iframe.attr('src') === '') {
            iframe.attr('src', iframe.attr('data-src'));
        }
    });
    $(document).on('click', results.selector + ' a.close-map', function() {
        var id = $(this).attr('data-id');
        $(this).hide();
        results.find("a.open-map[data-id='" + id + "']").show();
        results.find("div.map[data-id='" + id + "']").hide();
    });
});
