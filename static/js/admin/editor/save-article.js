/**
 * Saving the document
 */

var AUTOSAVE_FREQUENCY = 60; // Autosave every <this> seconds
var NO_SAVE_WARNING = 60 * 5; // Should never happen when this is larger than autosave frequency

$(document).ready(function() {

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 15) {
            $("div.edit-article-header div.save span.save-text").html('<i class="icon-ok"></i> Artikkelen er lagret.');
        } else {
            $("div.edit-article-header div.save span.save-text").html('<i class="icon-info-sign"></i> Autolagrer om ' + (AUTOSAVE_FREQUENCY - lastSaveCount) + ' sekunder.');
        }

        if(lastSaveCount == NO_SAVE_WARNING) {
            $("div.no-save-warning").show();
        }

        if(lastSaveCount >= AUTOSAVE_FREQUENCY) {
            $("div.edit-article-header div.save button.save").click();
            return;
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    $("div.edit-article-header div.save button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).attr('disabled', true);
        $("div.edit-article-header div.save span.save-text").html("<i class=\"icon-time\"></i> Lagrer, vennligst vent...");
        $("div.no-save-warning").hide();
        var rows = [];
        $("article div.row").each(function() {
            var row = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            rows = rows.concat([row]);
        });
        var columns = [];
        $("article div.column").each(function() {
            var column = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            columns = columns.concat([column]);
        });
        var contents = [];
        $("article div.html, article div.title, article div.lede").each(function() {
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: $(this).html()
            };
            contents = contents.concat([content]);
        });
        $("article div.image").each(function() {
            var anchor;
            if($(this).find('a').length == 0) {
                anchor = null;
            } else {
                anchor = $(this).find('a').attr('href');
            }
            var image = {
                src: $(this).find('img').attr('src'),
                alt: $(this).find('img').attr('alt'),
                anchor: anchor
            };
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: JSON.stringify(image)
            };
            contents = contents.concat([content]);
        });

        $.ajax({
            url: '/sherpa/cms/editor/' + $("article").attr('data-id') + '/',
            type: 'POST',
            data: "rows=" + encodeURIComponent(JSON.stringify(rows)) +
                  "&columns=" + encodeURIComponent(JSON.stringify(columns)) +
                  "&contents=" + encodeURIComponent(JSON.stringify(contents))
        }).done(function(result) {
            lastSaveCount = 0;
        }).fail(function(result) {
            // Todo
            $(document.body).html(result.responseText);
        }).always(function(result) {
            updateSaveCount();
            $("div.edit-article-header div.save button.save").removeAttr('disabled');
        });
    });

});
