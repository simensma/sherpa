$(document).ready(function() {

    $("div.loading").hide();
    $("div.no-results").hide();

    performSearch();
    $("input[type='radio']").change(performSearch);
    function performSearch() {
        var category = $("input[type='radio'][name='category']:checked").val();
        var county = $("input[type='radio'][name='county']:checked").val();
        $("table#results").children().remove();
        if(category == 'all' && county == 'all') {
            $("div.all").show();
            return $(this);
        } else {
            $("div.all").hide();
        }
        $("div.loading").show();
        $("div.no-results").hide();
        $.ajax({
            url: '/foreninger/filtrer/',
            type: 'POST',
            data: 'category=' + encodeURIComponent(category) +
                  '&county=' + encodeURIComponent(county)
        }).fail(function(result) {
            $(document.body).html(result.responseText);
        }).done(function(result) {
            result = JSON.parse(result);
            for(var i=0; i<result.length; i++) {
                $("table#results").append(result[i]);
            }
            if(result.length == 0) {
                $("div.no-results").show();
            }
            $("table#results div.map").hide();
            $("table#results a.close-map").hide();
        }).always(function() {
            $("div.loading").hide();
        });
    }

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
