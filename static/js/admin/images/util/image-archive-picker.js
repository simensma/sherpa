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
        showFolder('');
    });

    /* Events on DOM elements that come and go */

    $(document).on('click', 'div.image-archive-picker .clickable-album', function() {
        showFolder($(this).attr('data-id'));
    });

    $(document).on('click', 'div.image-archive-picker .clickable-mine', function() {
        showFolder('mine');
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
            $("div.image-archive-picker div.content").removeClass('simple-display');
        } else {
            $("div.image-archive-picker div.content").addClass('simple-display');
        }
    }

    function search() {
        var query = picker.find("input[name='search']").val();
        // Setting a default hardcoded search length here, in case we forgot
        // to provide it with js_globals - which we should rather do
        if(query.length < (window.IMAGE_SEARCH_LENGTH || 3)) {
            $("div.image-archive-picker div.too-few-chars").show();
        } else {
            var ajaxLoader = hideContent();
            $.ajax({
                url: $("div.image-archive-picker").attr("data-search-url"),
                data: { query: JSON.stringify(query) }
            }).done(function(result) {
                result = JSON.parse(result);
                $("div.image-archive-picker div.content").append(result.html);
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                ajaxLoader.remove();
            });
        }
    }

    function hideContent() {
        $("div.image-archive-picker div.too-few-chars").hide();
        var content = $("div.image-archive-picker div.content");
        content.empty();
        var ajaxLoader = $('<img class="ajaxloader" src="/static/img/ajax-loader-small.gif" alt="Laster, vennligst vent...">');
        content.append(ajaxLoader);
        return ajaxLoader;
    }

    function showFolder(album) {
        var ajaxLoader = hideContent();
        var url;
        if(album == 'mine') {
            url = $("div.image-archive-picker").attr("data-mine-url");
        } else {
            url = $("div.image-archive-picker").attr("data-album-url");
        }
        $.ajax({
            url: url,
            data: { album: JSON.stringify(album) }
        }).done(function(result) {
            result = JSON.parse(result);
            $("div.image-archive-picker div.content").append(result.html);
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            ajaxLoader.remove();
        });
    }

}(window.ImageArchivePicker = window.ImageArchivePicker || {}, jQuery ));
