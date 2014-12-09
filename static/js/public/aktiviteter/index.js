$(function() {
    var listing = $("div.aktivitet-listing");
    var filters = listing.find("div.search-filters");
    var button_selections = filters.find("div.button-selections");
    var category_type_wrapper = button_selections.filter('[data-dnt-container="category-types"]');
    var popups = listing.find("div.popups");
    var results = listing.find("div.results");
    var results_content = results.find("div.content");
    var results_fail = results.find("div.fail");
    var toggle_filters_and_results = listing.find('.toggle-filters-results');
    var column_filters = listing.find('.column-filters');
    var column_results = listing.find('.column-results');
    var filter_location = filters.find("select[name='location']");
    var filter_organizers = filters.find("select[name='organizers']");

    var device_is_mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);

    filters.find('[data-dnt-container="start-date"], [data-dnt-container="end-date"]').each(function (index, el) {
        if (device_is_mobile) {
            $(el).find('input').attr('type', 'date');

        } else {
            $(el).datepicker({
                format: 'dd.mm.yyyy',
                weekStart: 1,
                autoclose: true,
                startDate: today,
                forceParse: false
            });
        }
    });

    toggle_filters_and_results.find('button').bind('click', function (e) {
        var action = $(this).data('dnt-action');

        toggle_filters_and_results.find('button').show();
        $(this).hide();

        var listing_top = listing.offset().top;
        $(window).scrollTop(listing_top);

        if(action === 'show-activities-filters') {
            column_filters.removeClass('hidden-xs');
            column_results.addClass('hidden-xs');

        } else if(action === 'show-activities-results') {
            column_filters.addClass('hidden-xs');
            column_results.removeClass('hidden-xs');
        }
    });

    button_selections.find("button").click(function() {
        $(this).toggleClass('selected');
        if($(this).is('.selected')) {
            $(this).addClass('btn-danger');
        } else {
            $(this).removeClass('btn-danger');
        }
    });

    button_selections.filter(".categories").click(function() {
        category_type_wrapper.find('[data-dnt-container="category"]').slideUp('fast');
        category_type_wrapper.find('button.selected').removeClass('selected btn-danger');

        var selected = $(this).find('.selected');
        if(selected.length !== 1) {
            return $(this);
        }

        var category = selected.attr('data-category');
        category_type_wrapper.find('[data-dnt-category="' + category + '"]').slideDown('fast');
    });

    // Disable enter submit on forms
    filters.find("form").bind("keypress", function(e) {
        if(e.keyCode == 13) {
            refreshContent(results_content.attr('data-current-page'));
            return false;
        }
    });

    filters.find("button").click(function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    if (!device_is_mobile) {
        filter_location.select2();
    }

    filter_location.change(function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find('[data-dnt-container="start-date"],[data-dnt-container="end-date"]').on('change', function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    if (!device_is_mobile) {
        filter_organizers.select2();
    }

    filter_organizers.on('change', function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find('input[name="search"]').on('blur', function () {
        refreshContent(results_content.attr('data-current-page'));
    })

    $(document).on('click', results_content.selector + ' ul.pagination li:not(.disabled):not(.active) a.page', function() {
        refreshContent($(this).attr('data-page'), true);
    });

    function refreshContent(page, scrollToTop) {
        results_content.find("div.pagination li").addClass('disabled');
        results_content.find('a.aktivitet-item').addClass('disabled');
        results_content.find('a.aktivitet-item').click(function(e) { e.preventDefault(); });

        results_fail.hide();

        // Scroll to the top of the results which makes sense
        if (scrollToTop) {
            $('html, body').animate({
                scrollTop: $('.aktivitet-listing').offset().top
            }, 2000);
        }

        var filter = collectFilter();
        filter.page = page;
        $.ajaxQueue({
            url: results.attr('data-filter-url'),
            data: { filter: JSON.stringify(filter) }
        }).done(function(result) {
            result = JSON.parse(result);

            // Update list view
            results_content.attr('data-current-page', result.page);
            results_content.empty();
            results_content.append(result.html);

            // Force media-query style update since it listens only on size changes
            new ElementQueries().update();

            // Initiate tooltips
            results_content.find('[data-tooltip]').tooltip();

        }).fail(function(result) {
            results_content.empty();
            results_fail.show();
        }).always(function(result) {
            // we are done
        });
    }

    function collectFilter() {
        var categories = [];
        button_selections.filter(".categories").find("button.category.selected").each(function() {
            categories.push($(this).attr('data-category'));
        });
        var category_types = [];
        category_type_wrapper.find('button.selected').each(function() {
            category_types.push($(this).attr('data-dnt-category-type'));
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
        var organizers = [];
        filters.find("select[name='organizers'] option:selected").each(function() {
            organizers.push($(this).val());
        });
        var start_date = filters.find("input[name='start_date']").val();
        var end_date = filters.find("input[name='end_date']").val();
        var search = filters.find("input[name='search']").val();
        if (/[\d]{4}\-[\d]{2}\-[\d]{2}/.test(start_date)) {
            start_date = start_date.replace(/([\d]{4})\-([\d]{2})\-([\d]{2})/, '$3.$2.$1');
        }
        if (/[\d]{4}\-[\d]{2}\-[\d]{2}/.test(end_date)) {
            end_date = end_date.replace(/([\d]{4})\-([\d]{2})\-([\d]{2})/, '$3.$2.$1');
        }
        var lat_lng = filters.find("input[name='lat_lng']").val();
        return {
            categories: categories,
            category_types: category_types,
            audiences: audiences,
            difficulties: difficulties,
            locations: locations,
            start_date: start_date,
            end_date: end_date,
            search: search,
            organizers: organizers,
            lat_lng: lat_lng,
        };
    }

    $('input[name="ssr_id"]').select2({
        allowClear: true,
        placeholder: 'Finn sted',
        minimumInputLength: 2,
        escapeMarkup: function (m) { return m; },
        formatSearching: 'Søker...',
        formatNoMatches: 'Ingen treff i Kartverket!',
        formatInputTooShort: 'Minimum to bokstaver',
        formatResult: positionSsrToHtml,
        query: function(options) {
            var res = [];
            $.fn.SSR(options.term).done(function(steder) {
                res = $.map(steder.stedsnavn, function(sted) {
                    sted.id = sted.ssrId;
                    sted.text = sted.stedsnavn;
                    return sted;
                });
            }).always(function() { options.callback({results: res}); });
        }
    }).on('change', function(e) {
        if(e.added) {
            $("input[name='lat_lng']").val(e.added.nord + ',' + e.added.aust);
        } else {
            $("input[name='lat_lng']").val('');
        }
        refreshContent(0);
    });

    function positionSsrToHtml(sted) {
        return [
            '<label>' + sted.text + '</label><br>',
            '<small>' + [sted.navnetype, sted.kommunenavn, sted.fylkesnavn].join(' i ') + '</small>'
        ].join('');
    };
});
