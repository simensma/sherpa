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
            $("div.editor-header div.save span.save-text").html('<i class="icon-ok"></i> Lagret.');
        } else {
            $("div.editor-header div.save span.save-text").html('<i class="icon-info-sign"></i> Autolagrer om ' + (AUTOSAVE_FREQUENCY - lastSaveCount) + ' sekunder.');
        }

        if(lastSaveCount == NO_SAVE_WARNING) {
            $("div.no-save-warning").show();
        }

        if(lastSaveCount >= AUTOSAVE_FREQUENCY) {
            $("div.editor-header div.save button.save").click();
            return;
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    function collectRows() {
        var rows = []
        $("article > div.row-fluid").each(function() {
            var row = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            rows = rows.concat([row]);
        });
        return rows;
    }

    function collectColumns() {
        var columns = [];
        $("article div.column").each(function() {
            var column = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            columns = columns.concat([column]);
        });
        return columns;
    }

    function collectContents() {
        var contents = [];
        $("article > div.row-fluid > div.column > div.html, article > div.row-fluid > div.column > div.title, article > div.row-fluid > div.column > div.lede").each(function() {
            if($(this).is('[data-placeholder]')) {
                var html = '';
            } else {
                var html = $(this).html();
            }
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: html
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
                style: $(this).find('img').attr('style'),
                selection: $(this).find('img').attr('selection'),
                parentHeight: $(this).find('img').attr('parentHeight'),
                description: $(this).find('span.description').text(),
                photographer: $(this).find('span.photographer span.content').text(),
                anchor: anchor
            };
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: JSON.stringify(image)
            };
            contents = contents.concat([content]);
        });
        return contents;
    }

    $("div.editor-header div.save button.save").click(save);
    $("div.editor-header div.save button.preview").click(function() {
        $(this).html('<i class="icon-search"></i> Lagrer først, vennligst vent...');
        $(this).attr('disabled', true);
        var url = $(this).attr('data-href');
        save(function() {
            window.location = url;
        });
    });

    window.save = save;
    function save(callback) {
        clearInterval(updateSaveCountID);
        $("div.editor-header div.save button.save").attr('disabled', true);
        $("div.editor-header div.save span.save-text").html("<i class=\"icon-time\"></i> Lagrer, vennligst vent...");
        $("div.no-save-warning").hide();
        $.ajaxQueue({
            url: '/sherpa/cms/editor/' + $("article").attr('data-id') + '/',
            data: "rows=" + encodeURIComponent(JSON.stringify(collectRows())) +
                  "&columns=" + encodeURIComponent(JSON.stringify(collectColumns())) +
                  "&contents=" + encodeURIComponent(JSON.stringify(collectContents()))
        }).done(function(result) {
            lastSaveCount = 0;
            if(typeof(callback) == 'function') {
                callback();
            }
        }).fail(function(result) {
            // Todo
            $(document.body).html(result.responseText);
        }).always(function(result) {
            updateSaveCount();
            $("div.editor-header div.save button.save").removeAttr('disabled');
        });
    }

});
