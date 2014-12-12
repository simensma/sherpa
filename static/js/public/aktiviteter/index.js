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
    var filter_omrader = filters.find("select[name='omrader']");
    var filter_organizers = filters.find("select[name='organizers']");
    var reset_search_section = listing.find('.section.reset-search');

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

    filters.find('button:not([data-dnt-action="show-activities-results"])').click(function() {
        // We use setTimeout here to make sure this is put at the end of JavaScript the event loop.
        // This is beacause there are other event listeners for some of these buttons that need to
        // do their work before we update the result.
        // Recommended reading: http://strongloop.com/strongblog/node-js-event-loop/
        setTimeout(function() { refreshContent(results_content.attr('data-current-page')); }, 0);
    });

    if (device_is_mobile) {
        filter_omrader.find('option[value=""]').remove();
        filter_omrader.on('change', function() {
            filter_omrader.parents('.input-group-hidden-addon').first().removeClass('input-group-hidden-addon').addClass('input-group');
            filter_omrader.nextAll('.input-group-addon').first().removeClass('jq-hide');
            // Using show() will not work here, as the element should be display: table-cell
        });
        filter_omrader.nextAll('.input-group-addon[data-dnt-action="empty-field"]').click(function() {
            filter_omrader.val([]);
            refreshContent(results_content.attr('data-current-page'));
        });

    } else {
        filter_omrader.select2();
    }

    filter_omrader.change(function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find('[data-dnt-container="start-date"],[data-dnt-container="end-date"]').on('change', function() {
        // TODO: This is triggered twice if date is changed using bootstrap datepicker, should be fixed
        refreshContent(results_content.attr('data-current-page'));
    });

    if (device_is_mobile) {
        filter_organizers.find('option[value=""]').remove();
        filter_organizers.on('change', function() {
            filter_organizers.parents('.input-group-hidden-addon').first().removeClass('input-group-hidden-addon').addClass('input-group');
            filter_organizers.nextAll('.input-group-addon').first().removeClass('jq-hide');
            // Using show() will not work here, as the element should be display: table-cell
        });
        filter_organizers.nextAll('.input-group-addon[data-dnt-action="empty-field"]').click(function() {
            filter_organizers.val([]);
            refreshContent(results_content.attr('data-current-page'));
        });

    } else {
        filter_organizers.select2();
    }

    filter_organizers.on('change', function() {
        refreshContent(results_content.attr('data-current-page'));
    });

    filters.find('input[name="search"]').on('blur', function () {
        refreshContent(results_content.attr('data-current-page'));
    }).on('keypress', function(e) {
        if(e.which === 13) { // Enter
            $(this).blur();
        }
    });

    $(document).on('click', results_content.selector + ' .pagination :not(.disabled):not(.active) a.page', function() {
        refreshContent($(this).attr('data-page'), true);
    });

    function updateUrl(filter) {
        var keys  = Object.keys(filter),
            query = [], i;

        for (i = 0; i < keys.length; i++) {
            if (filter[keys[i]] !== '' && !(keys[i] === 'page' && filter[keys[i]] === '1')) {
                query.push(keys[i] + '=' + filter[keys[i]]);
            }
        }

        history.pushState(null, null, '?' + query.join('&'));
    }

    function refreshContent(page, scrollToTop) {
        if (page === 0) {
            toggle_filters_and_results.addClass('progress-bar progress-bar-striped active');
        }

        results_content.find("div.pagination li").addClass('disabled');
        results_content.find('a.aktivitet-item').addClass('disabled');
        results_content.find('a.aktivitet-item').click(function(e) { e.preventDefault(); });

        results_fail.hide();
        reset_search_section.show();

        // Scroll to the top of the results which makes sense
        if (scrollToTop) {
            $('html, body').animate({
                scrollTop: $('.aktivitet-listing').offset().top
            }, 1000);
        }

        var filter = collectFilter(page);

        // Here we set the new URL so that user can go back
        updateUrl(filter);

        $.ajaxQueue({
            url: results.attr('data-filter-url'),
            data: filter
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

            updateResultsCount();

            togglePositionSearchWarning();

            toggle_filters_and_results.removeClass('progress-bar progress-bar-striped active');

        }).fail(function(result) {
            results_content.empty();
            results_fail.show();
            updateResultsCount();
        }).always(function(result) {
            // we are done
        });
    }

    function togglePositionSearchWarning() {
        var is_position_search = !!$('[name="ssr_id"]').val();
        if (is_position_search) {
            $('.alert.alert-warning.position-search-warning').show();

        } else {
            $('.alert.alert-warning.position-search-warning').hide();
        }
    }

    function updateResultsCount() {
        var results_count = results_content.find('.listing-container').attr('data-dnt-listing-total-results-count');
        $('.toggle-filters-results .aktiviteter-result-total-count').html(results_count);
    }
    updateResultsCount();

    function collectFilter(page) {
        res = {page: page};

        res.categories = button_selections.filter(".categories").find("button.category.selected").map(function() {
            return $(this).attr('data-category');
        }).get().join();

        res.category_types = category_type_wrapper.find('button.selected').map(function() {
            return $(this).attr('data-dnt-category-type');
        }).get().join();

        res.audiences = button_selections.filter(".audiences").find("button.audience.selected").map(function() {
            return $(this).attr('data-audience');
        }).get().join();

        res.difficulties = button_selections.filter(".difficulties").find("button.difficulty.selected").map(function() {
            return $(this).attr('data-difficulty');
        }).get().join();

        res.omrader = filters.find("select[name='omrader'] option:selected").map(function() {
            return $(this).val();
        }).get().join();

        res.organizers = filters.find("select[name='organizers'] option:selected").map(function() {
            return $(this).val();
        }).get().join();

        res.start_date = filters.find("input[name='start_date']").val();
        res.end_date = filters.find("input[name='end_date']").val();
        res.search = filters.find("input[name='search']").val();
        if (/[\d]{4}\-[\d]{2}\-[\d]{2}/.test(res.start_date)) {
            res.start_date = res.start_date.replace(/([\d]{4})\-([\d]{2})\-([\d]{2})/, '$3.$2.$1');
        }
        if (/[\d]{4}\-[\d]{2}\-[\d]{2}/.test(res.end_date)) {
            res.end_date = res.end_date.replace(/([\d]{4})\-([\d]{2})\-([\d]{2})/, '$3.$2.$1');
        }
        res.lat_lng = filters.find("input[name='lat_lng']").val();

        return res;
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
