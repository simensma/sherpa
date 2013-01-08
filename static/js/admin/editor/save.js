/**
 * Saving the document
 */

var NO_SAVE_WARNING = 60 * 5;

$(document).ready(function() {

    var lastSaveCount = 0;
    var updateSaveCountID;
    var statusIcon = '<i class="icon-heart"></i>';
    function updateSaveCount() {
        lastSaveCount += 1;
        $("div.editor-header button.save").html(statusIcon + ' Lagre nå (' + lastSaveCount + ')');

        if(lastSaveCount == NO_SAVE_WARNING) {
            $("div.no-save-warning").show();
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

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
        $("div.no-save-warning").hide();

        var data = {};

        // Rows
        var rows = []
        $("article > div.row-fluid").each(function() {
            var row = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            rows.push(row);
        });
        data.rows = JSON.stringify(rows);

        // Columns
        var columns = [];
        $("article div.column").each(function() {
            var column = {
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            };
            columns.push(column);
        });
        data.columns = JSON.stringify(columns);

        // Contents
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
        data.contents = JSON.stringify(contents);

        var parent_select = $("div.editor-header.page select[name='parent']");
        if($("div.editor-header.page").length > 0) {
            /* Page-specific */

            // Title
            data.title = $("div.editor-header.page input[name='title']").val();

            // Parent page
            data.parent = parent_select.find("option:selected").val();

            // Whether or not to display ads
            data.ads = JSON.stringify($("div.editor-header.page input[name='display-ads']:checked").length > 0);

            // Publish-state
            data.datetime= $("input[name='page-datetime-field']").val();
            data.status= JSON.stringify($("div.editor-header input[name='publish']:checked").length > 0);
        } else if($("div.editor-header.article").length > 0) {
            /* Article-specific */

            // Authors
            var authors = [];
            $("select[name='authors'] > option:selected").each(function() {
                authors.push($(this).val());
            });
            data.authors = JSON.stringify(authors);

            // Publish-state
            data.datetime = $("input[name='article-datetime-field']").val();
            data.status = JSON.stringify({'status': $("div.editor-header input[name='publish']:checked").length > 0});

            // Tags
            data.tags = JSON.stringify(article_tagger.tags);
        }

        // Save content
        $.ajaxQueue({
            url: '/sherpa/cms/editor/lagre/' + $("div.editor-header").attr('data-version-id') + '/',
            data: data
        }).done(function(result) {
            result = JSON.parse(result);

            lastSaveCount = 0;
            statusIcon = '<i class="icon-heart"></i>';
            saveButton.removeClass('btn-danger').addClass('btn-success');
            if(typeof(done) == 'function') {
                done();
            }

            // Parent page-response
            if(result.parent_error == 'parent_in_parent') {
                alert('Du kan ikke velge den foreldresiden, fordi *den* allerede er en underside av denne siden.');
                parent_select.val(parent_select.find("option.default").val());
                parent_select.trigger('liszt:updated');
            } else {
                parent_select.find("option.default").removeClass('default');
                parent_select.find("option:selected").addClass('default');
            }

            // Article-authors response
            if(result.author_error == 'no_authors') {
                alert("Artikkelforfattere ble ikke endret; du må velge minst én forfatter!");
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
            updateSaveCount();
            saveButton.removeAttr('disabled');
        });

    }

});
