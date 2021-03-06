$(function() {

    var marker, map;

    function positionSsrSelectShowHandler() {
        $(this).find('input').select2({
            placeholder: 'Hvor starter turen?',
            minimumInputLength: 2,
            escapeMarkup: function (m) { return m; },
            formatSearching: function () { return 'Søker'; },
            formatInputTooShort: function (term, minLength) { return 'Minimum to bokstaver'; },
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
        }).select2('open');
    };

    function positionSsrToHtml(sted) {
        return [
            '<label>' + sted.text + '</label><br>',
            '<small>' + [sted.navnetype, sted.kommunenavn, sted.fylkesnavn].join(' i ') + '</small>'
        ].join('');
    };

    function positionNtbSelectShowHandler() { };

    function positionMapInit() {
        if (map) { return; }

        var tile_url = [
            'http://opencache.statkart.no/gatekeeper/gk/',
            'gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}'
        ].join('');

        map = L.map('map', {
            dragging: false,
            zoomControl: false,
            scrollWheelZoom: false,
            closePopupOnClick: false,
            layers: [L.tileLayer(tile_url, {attribution: 'Kartverket'})]
        });
    };

    function positionMapMarkerUpdate() {
        if (!map) { return; }

        var latlng = $(this).val().split(',');

        if (latlng[0], latlng[1]) {
            latlng = new L.LatLng(latlng[0], latlng[1]);

            if (marker) {
                marker.setLatLng(latlng);
            } else {
                marker = L.marker(latlng, {title: 'Turen går her'}).addTo(map);
            }

            // @TODO what to put in the popup
            marker.bindPopup('Her starter turen', {closeButton: false});
            map.setView(latlng, 12, {reset: true});
            marker.openPopup()
        }
    };

    function positionLatlngDomUpdate(e) {
        var lat, lng;
        if (e.data.type === 'ssr') {
            lat = $(this).select2('data').nord;
            lng = $(this).select2('data').aust;
        } else {
            throw new Error('Type not supported');
        }

        $('input[name="latlng"]').val(lat + ',' + lng).trigger("change");
    }

    function positionMetadataRegenerate(e) {
        var latlng = $(this).val().split(',');

        if (latlng.length === 2) {
            positionMetadataSelect.apply($('select[name="counties"]'), latlng);
            positionMetadataSelect.apply($('select[name="municipalities"]'), latlng);
            positionMetadataSelect.apply($('select[name="omrader"]'), latlng);
        }
    };

    function positionMetadataSelect(lat, lng) {
        // @TODO this depends on the dom
        $(this).parent().parent().find('.ajaxloader').removeClass('jq-hide');

        $.ajaxQueue({
            url: $(this).data('lookupUrl'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            $(this).find('option:selected').prop('selected', false);
            result = JSON.parse(result);
            for (var i = 0; i < result.length; i++) {
                $(this).find('option[value="' + result[i] + '"]').prop('selected', true);
            }
            $(this).trigger('chosen:updated');
        }.bind(this)).fail(function() {
            // @TODO handle this
        }.bind(this)).always(function() {
            // @TODO this depends on the dom
            $(this).parent().parent().find('.ajaxloader').addClass('jq-hide');
        }.bind(this));
    };

    function positionMetadataPlaceholderUpdate(e) {
        var html = $.map($(this).find('option:selected'), function(option) {
            return $(option).html().trim();
        }).join(', ');
        $('[data-placeholder-for="' + e.data.placeholder + '"]').html(html || 'Ingen funnet');
    };

    $.fn.showWithEvents = function() {
        $(this).trigger('preshow').removeClass('jq-hide').trigger('postshow');
    };

    $.fn.hideWithEvents = function() {
        $(this).trigger('prehide').addClass('jq-hide').trigger('postshow');
    };

    function defaultDataClickShowHandler(e) {
        e.preventDefault();
        $.each($(this).data('clickShow').split(' '), function(index, container) {
            $('[data-container="' + container + '"]').showWithEvents();
        });
    };

    function defaultDataClickHideHandler(e) {
        e.preventDefault();
        $.each($(this).data('clickHide').split(' '), function(index, container) {
            $('[data-container="' + container + '"]').hideWithEvents();
        });
    };

    function defaultDataSelectShowHandler() {
        $.each($(this).data('selectShow').split(' '), function(index, container) {
            $('[data-container="' + container + '"]').showWithEvents();
        });
    };

    $(document).on('click', '[data-click-show]', defaultDataClickShowHandler);
    $(document).on('click', '[data-click-hide]', defaultDataClickHideHandler);
    $(document).one('postshow', '[data-container="position-ssr-select"]', positionSsrSelectShowHandler);
    $(document).one('postshow', '[data-container="position-ntb-select"]', positionNtbSelectShowHandler);

    $(document).one('select2-selecting', 'input[name="ssr_id"]', defaultDataSelectShowHandler);
    $(document).one('select2-selecting', 'input[name="ntb_id"]', defaultDataSelectShowHandler);

    $(document).one('postshow', '[data-container="position-map"]', positionMapInit);

    $(document).on('change', 'input[name="ssr_id"]', {type: 'ssr'}, positionLatlngDomUpdate);
    $(document).on('change', 'input[name="ntb_id"]', {type: 'ntb'}, positionLatlngDomUpdate);

    $(document).on('change', 'input[name="latlng"]', positionMapMarkerUpdate);
    $(document).on('change', 'input[name="latlng"]', positionMetadataRegenerate);

    $(document).on('chosen:updated', 'select[name="municipalities"]', {placeholder: 'municipality'} , positionMetadataPlaceholderUpdate);
    $(document).on('chosen:updated', 'select[name="counties"]'      , {placeholder: 'county'}       , positionMetadataPlaceholderUpdate);
    $(document).on('chosen:updated', 'select[name="omrader"]'       , {placeholder: 'omrade'}       , positionMetadataPlaceholderUpdate);

    if (/^\d+(\.\d+)?,\d+(\.\d+)?$/.test($('input[name="latlng"]').val())) {
        $(document).one('postshow', '[data-container="position-map"]', positionMapMarkerUpdate.bind($('input[name="latlng"]')));
        $('[data-container="position-map"]').showWithEvents();
        $('[data-container="position-metadata"]').showWithEvents();
    }
});
