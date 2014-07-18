$(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var position_section = editor.find("div.section.position");
    var map_container = position_section.find("div.map-container");
    // var popup_content = position_section.find("div.popup-content").html();
    var show_map_button = position_section.find("a.show-map");

    var counties_select = position_section.find("select[name='counties']");
    var counties_ajaxloader = counties_select.nextAll("img.ajaxloader");
    var municipalities_select = position_section.find("select[name='municipalities']");
    var municipalities_ajaxloader = municipalities_select.nextAll("img.ajaxloader");
    var locations_select = position_section.find("select[name='locations']");
    var locations_ajaxloader = locations_select.nextAll("img.ajaxloader");

    var marker, map;

    var init_map = function(opts) {
      if (map) { return; }

      map = L.map('map', {
        dragging: false,
        zoomControl: false,
        scrollWheelZoom: false,
        closePopupOnClick: false,
        layers: [
          L.tileLayer('http://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo2&zoom={z}&x={x}&y={y}', {
              attribution: 'Kartverket'
          })
        ]
      });

      if (opts && opts.set_default_view) { map.setView([65, 12], 5); }
    };

    var set_map_marker = function(sted) {
      if (!map || (marker && marker.ssr_id === sted.id)) { return; }

      //lat = lat || Turistforeningen.start_point_lat;
      //lon = lon || Turistforeningen.start_point_lng;

      if (sted.nord && sted.aust) {
        var latlng = new L.LatLng(sted.nord, sted.aust);

        if (marker) {
          marker.setLatLng(latlng);
        } else {
          marker = L.marker(latlng, {title: 'Turern starter her'}).addTo(map);
        }

        marker.ssr_id = sted.id
        marker.bindPopup(
          '<strong>' + sted.text + '</strong><br>' +
          '<small>' + sted.navnetype + ' i ' + sted.kommunenavn + ' i ' + sted.fylkesnavn + '</small>'
        , {
          closeOnClick: false,
          closeButton: false
        });
        map.setView(latlng, 12, {reset: true});
        marker.openPopup()

        set_map_marker_dom(marker);
      }
    };

    var set_map_marker_dom = function(marker) {
      form.find("input[name='position_lat']").val(marker.getLatLng().lat);
      form.find("input[name='position_lng']").val(marker.getLatLng().lng);
    };

    var show_location_picker = function(e) {
      $('.find-location').removeClass('jq-hide');
      $('.find-location input').select2({
        placeholder: 'Hvor starter turen?',
        minimumInputLength: 2,
        escapeMarkup: function (m) { return m; },
        formatSearching: function () { return 'Søker'; },
        formatInputTooShort: function (term, minLength) { return 'Minimum to bokstaver'; },
        formatResult: function(obj) {
          return '<label>' + obj.text + '</label><br>'
               + '<small>' + obj.navnetype + ' i ' + obj.kommunenavn + ' i ' + obj.fylkesnavn + '</small>';
        },
        query: location_picker_query
      }).on('change', function(e) {
        if (e.added) { show_and_set_map_marker(e.added); }

      }).select2('open');
    };

    var location_picker_query = function(options) {
      var req, res;

      res = [];

      req = $.fn.SSR(options.term);

      req.done(function(steder) {
        if (steder.stedsnavn && steder.stedsnavn.length > 0) {
          for (var i = 0; i < steder.stedsnavn.length; i++) {
            steder.stedsnavn[i].id = steder.stedsnavn[i].ssrId;
            steder.stedsnavn[i].text = steder.stedsnavn[i].stedsnavn;
          }

          res = steder.stedsnavn;
        }
      });

      req.always(function() {
        options.callback({results: res});
      });
    };

    function show_and_set_map_marker(sted) {
      map_container.show(function() {
        init_map({set_default_view: false});
        set_map_marker(sted);
      });
      var map_top = $(map_container).offset().top;
      $('html, body').animate({scrollTop:(map_top - 80)}, '500', 'swing', function() {});
    };

    // Show location autocomplete
    $(document).on('click', '[data-toggle="location-select-show"]', show_location_picker);


    function county_lookup(lat, lng) {
        counties_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-county-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            counties_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                counties_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            counties_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            counties_ajaxloader.hide();
        });
    }

    function municipality_lookup(lat, lng) {
        municipalities_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-municipality-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            municipalities_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                municipalities_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            municipalities_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            municipalities_ajaxloader.hide();
        });
    }

    function location_lookup(lat, lng) {
        locations_ajaxloader.show();
        $.ajaxQueue({
            url: position_section.attr('data-location-lookup-url'),
            data: {
                lat: JSON.stringify(lat),
                lng: JSON.stringify(lng)
            }
        }).done(function(result) {
            result = JSON.parse(result);
            locations_select.find("option:selected").prop('selected', false);
            for(var i=0; i<result.length; i++) {
                locations_select.find("option[value='" + result[i] + "']").prop('selected', true);
            }
            locations_select.trigger("chosen:updated");
        }).fail(function() {
            // TODO
        }).always(function() {
            locations_ajaxloader.hide();
        });
    }

    // DEMO: Simple toggling of fields, for demo purposes only

    $(document).on('click', '[data-toggle="counties-edit-show"]', function () {
        position_section.find('.counties-static').addClass('jq-hide');
        position_section.find('.counties-edit').removeClass('jq-hide');
    });

    $(document).on('click', '[data-toggle="municipalities-edit-show"]', function () {
        position_section.find('.municipalities-static').addClass('jq-hide');
        position_section.find('.municipalities-edit').removeClass('jq-hide');
    });

    $(document).on('click', '[data-toggle="locations-edit-show"]', function () {
        position_section.find('.locations-static').addClass('jq-hide');
        position_section.find('.locations-edit').removeClass('jq-hide');
    });

    $(document).on('click', '[data-toggle="turforslag-select-show"]', function () {
        position_section.find('.find-turforslag').removeClass('jq-hide');
    });

});
