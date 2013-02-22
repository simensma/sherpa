(function(ImageArchivePicker, $, undefined ) {

    /* Pick up DOM elements and bind events */

    var picker;
    $(document).ready(function() {
        picker = $("div.image-archive-picker");

        // Bind events to functionality

        picker.find("input[name='include_meta']").change(setDisplayStatus);
        picker.find("button.image-search").click(search);
        picker.find("input[name='search']").keydown(function(e) {
            if(e.which == 13) { // Enter
                search();
            }
        });

        // The initial search
        performLookup(picker.attr("data-album-url"), { album: JSON.stringify('') });
    });

    /* Events on DOM elements that come and go */

    $(document).on('click', 'div.image-archive-picker .clickable-album', function() {
        var url = $("div.image-archive-picker").attr("data-album-url");
        var data = { album: JSON.stringify($(this).attr('data-id')) };
        performLookup(url, data);
    });

    $(document).on('click', 'div.image-archive-picker .clickable-mine', function() {
        var url = $("div.image-archive-picker").attr("data-mine-url");
        var data = { album: JSON.stringify('mine') };
        performLookup(url, data);
    });

    $(document).on('click', 'div.image-archive-picker .clickable-image', function() {
        var url = "http://cdn.turistforeningen.no/images/" + $(this).attr('data-path');
        var description = $(this).attr('data-description');
        var photographer = $(this).attr('data-photographer');

        picker.modal('hide');
        ImageArchivePicker.callback(url.trim(), description.trim(), photographer.trim());
    });

    /* Public methods */

    ImageArchivePicker.pick = function(callback) {
        ImageArchivePicker.callback = callback;
        archiveCallback = callback;
        picker.modal();
    };

    /* Private methods */

    // Set include_meta status with a class on the content div wrapper
    function setDisplayStatus() {
        if($(this).is(":checked")) {
            picker.find("div.content").removeClass('simple-display');
        } else {
            picker.find("div.content").addClass('simple-display');
        }
    }

    function search() {
        var query = picker.find("input[name='search']").val();
        // Setting a default hardcoded search length here, in case we forgot
        // to provide it with js_globals - which we should rather do
        if(query.length < (window.IMAGE_SEARCH_LENGTH || 3)) {
            picker.find("div.too-few-chars").show();
        } else {
            var url = picker.attr("data-search-url");
            var data = { query: JSON.stringify(query) };
            performLookup(url, data);
        }
    }

    function performLookup(url, data) {
        picker.find("div.too-few-chars").hide();
        var content = picker.find("div.content");
        content.empty();
        var ajaxLoader = $('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
        content.append(ajaxLoader);

        $.ajax({
            url: url,
            data: data
        }).done(function(result) {
            result = JSON.parse(result);
            picker.find("div.content").append(result.html);
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            ajaxLoader.remove();
        });
    }

}(window.ImageArchivePicker = window.ImageArchivePicker || {}, jQuery ));
