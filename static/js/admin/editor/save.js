/**
 * Saving the document
 */

var AUTOSAVE_FREQUENCY = 60; // Autosave every <this> seconds

$(document).ready(function() {

    var lastSaveCount = 0;
    var updateSaveCountID;
    var statusIcon = '<i class="icon-heart"></i>';
    function updateSaveCount() {
        lastSaveCount += 1;
        $("div.editor-header button.save").html(statusIcon + ' Lagre nå (' + (AUTOSAVE_FREQUENCY - lastSaveCount) + ')');

        if(lastSaveCount >= AUTOSAVE_FREQUENCY) {
            $("div.editor-header button.save").click();
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
            rows.push(row);
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
            columns.push(column);
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
            contents.push(content);
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
                selection: $(this).find('img').attr('data-selection'),
                ratioWidth: $(this).find('img').attr('data-ratio-width'),
                ratioHeight: $(this).find('img').attr('data-ratio-height'),
                parentHeight: $(this).find('img').attr('data-parentHeight'),
                description: $(this).find('span.description').text(),
                photographer: $(this).find('span.photographer span.content').text(),
                anchor: anchor
            };
            var content = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                content: JSON.stringify(image)
            };
            contents.push(content);
        });
        return contents;
    }

    $("div.editor-header button.save").click(save);
    $("div.editor-header button.preview").click(function() {
        var button = $(this);
        button.html('<i class="icon-search"></i> Lagrer først, vennligst vent...');
        button.attr('disabled', true);
        var url = $(this).attr('data-href');
        save(function() {
            window.location = url;
        }, function() {
            button.html('<i class="icon-search"></i> Forhåndsvisning');
            button.removeAttr('disabled');
        });
    });

    window.save = save;
    function save(done, fail) {
        clearInterval(updateSaveCountID);
        var saveButton = $("div.editor-header button.save");
        saveButton.attr('disabled', true);
        saveButton.html('<i class="icon-heart"></i> Lagrer...');

        // Save content
        $.ajaxQueue({
            url: '/sherpa/cms/editor/' + $("article").attr('data-id') + '/',
            data: "rows=" + encodeURIComponent(JSON.stringify(collectRows())) +
                  "&columns=" + encodeURIComponent(JSON.stringify(collectColumns())) +
                  "&contents=" + encodeURIComponent(JSON.stringify(collectContents()))
        }).done(function(result) {
            statusIcon = '<i class="icon-heart"></i>';
            saveButton.removeClass('btn-danger').addClass('btn-success');
            if(typeof(done) == 'function') {
                done();
            }
        }).fail(function(result) {
            statusIcon = '<i class="icon-warning-sign"></i>';
            alert("Whoops!\n\nVi klarte ikke å lagre innholdet. Er du sikker på at du har nettilgang?\n" +
                "Du kan prøve igjen til det går.\n\n" +
                "Hvis du lukker siden, vil du miste alle endringene siden sist du lagret.");
            saveButton.removeClass('btn-success').addClass('btn-danger');
            if(typeof(fail) == 'function') {
                fail();
            }
        }).always(function(result) {
            lastSaveCount = 0;
            updateSaveCount();
            saveButton.removeAttr('disabled');
        });

        // Page-specific saving
        if($("div.editor-header.page").length > 0) {
            // Save whether or not to display ads
            var value = $("div.editor-header.page input[name='display-ads']:checked").length > 0;
            $.ajaxQueue({
                url: '/sherpa/cms/side/annonser/' + $("article").attr('data-id') + '/',
                data: 'ads=' + encodeURIComponent(JSON.stringify(value))
            });
        }

        // Article-specific saving
        if($("div.editor-header.article").length > 0) {
            // Save authors
            var authors = [];
            var selected = $("select[name='authors'] > option:selected");
            if(selected.length == 0) {
                alert("Artikkelforfattere ble ikke endret; du må velge minst én forfatter!");
                return;
            }
            selected.each(function() {
                authors.push($(this).val());
            });
            $.ajaxQueue({
                url: '/sherpa/nyheter/forfattere/' + $("article").attr('data-id') + '/',
                data: 'authors=' + encodeURIComponent(JSON.stringify(authors))
            }).always(function() {
                $("button.save-authors").removeAttr('disabled');
            });

            // Publish-state
            $.ajaxQueue({
                url: '/sherpa/nyheter/publiser/' + $("div.editor-header").attr('data-id') + '/',
                data: {
                    datetime : encodeURIComponent($("input[name='article-datetime-field']").val()),
                    status : encodeURIComponent(JSON.stringify({'status': $("div.editor-header input[name='publish']:checked").length > 0}))
                }
            });

            // Save tags
            $.ajaxQueue({
                url: '/sherpa/nyheter/nokkelord/' + $("article").attr('data-id') + '/',
                data: 'tags=' + encodeURIComponent(JSON.stringify(tagger.tags))
            });
        }
    }

});
