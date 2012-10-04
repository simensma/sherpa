$(document).ready(function() {
    /* Toggle maps */
    $(document).on('click', 'table#results a.open-map', function() {
        var id = $(this).attr('data-id');
        $(this).hide();
        $("table#results a.close-map[data-id='" + id + "']").show();
        $("table#results div.map[data-id='" + id + "']").show();
        // Actually load the iframe
        var iframe = $("table#results div.map[data-id='" + id + "'] iframe");
        if(iframe.attr('src') == '') {
            iframe.attr('src', iframe.attr('data-src'));
        }
    });
    $(document).on('click', 'table#results a.close-map', function() {
        var id = $(this).attr('data-id');
        $(this).hide();
        $("table#results a.open-map[data-id='" + id + "']").show();
        $("table#results div.map[data-id='" + id + "']").hide();
    });
});
