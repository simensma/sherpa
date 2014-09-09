$(function() {
    var listing = $("div.aktivitet-listing");
    var filters = listing.find("div.search-filters");
    var button_selections = filters.find("div.button-selections");
    var popups = listing.find("div.popups");
    var results = listing.find("div.results");
    var results_content = results.find("div.content");
    var results_loading = results.find("div.loading");
    var results_fail = results.find("div.fail");

    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
    filters.find("div.input-append.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        startDate: today,
        forceParse: false
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

    button_selections.find("button").click(function() {
        $(this).toggleClass('selected');
        if($(this).is('.selected')) {
            $(this).addClass('btn-danger');
        } else {
            $(this).removeClass('btn-danger');
        }
    });

    button_selections.find("button").click(function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find("select[name='location']").change(function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find("div.input-append.date").on('changeDate', function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    $(document).on('click', results_content.selector + ' div.pagination li:not(.disabled):not(.active) a.page', function() {
        refreshContent($(this).attr('data-page'));
    });

    function refreshContent(page) {
        results_content.find("div.pagination li").addClass('disabled');
        results_loading.show();
        results_fail.hide();
        var filter = collectFilter();
        filter.page = page;
        $.ajaxQueue({
            url: results.attr('data-filter-url'),
            data: { filter: JSON.stringify(filter) }
        }).done(function(result) {
            result = JSON.parse(result);
            results_content.attr('data-current-page', result.page);
            results_content.empty();
            results_content.append(result.html);
        }).fail(function(result) {
            results_content.empty();
            results_fail.show();
        }).always(function(result) {
            results_loading.hide();
        });
    }

    function collectFilter() {
        var categories = [];
        button_selections.filter(".categories").find("button.category.selected").each(function() {
            categories.push($(this).attr('data-category'));
        });
        var audiences = [];
        button_selections.filter(".audiences").find("button.audience.selected").each(function() {
            audiences.push($(this).attr('data-audience'));
        });
        var difficulties = [];
        button_selections.filter(".difficulties").find("button.difficulty.selected").each(function() {
            difficulties.push($(this).attr('data-difficulty'));
        });
        var locations = [];
        filters.find("select[name='location'] option:selected").each(function() {
            locations.push($(this).val());
        });
        var travel_date = filters.find("input[name='travel_date']").val();
        return {
            categories: categories,
            audiences: audiences,
            difficulties: difficulties,
            locations: locations,
            travel_date: travel_date,
        };
    }
});