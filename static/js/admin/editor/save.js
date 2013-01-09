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

        // Element selectors
        var article_element = $("article");
        var row_elements = article_element.children("div.row-fluid");
        var column_elements = row_elements.children("div.column");
        var content_elements = column_elements.children("div.content");

        // Rows
        var rows = []
        row_elements.each(function() {
            rows.push({
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length
            });
        });
        data.rows = JSON.stringify(rows);

        // Columns
        var columns = [];
        column_elements.each(function() {
            var contained_elements = [];
            $(this).children('[data-id]').each(function() {
                // This is used server-side to delete items, so be pretty fucking sure that everything is included
                contained_elements.push($(this).attr('data-id'));
            });
            columns.push({
                id: $(this).attr('data-id'),
                order: $(this).prevAll().length,
                contained_elements: contained_elements
            });
        });
        data.columns = JSON.stringify(columns);

        // Contents
        var contents = [];
        var contents_awaiting_id = [];
        content_elements.filter(".html,.title,.lede").each(function() {
            var content = {
                order: $(this).prevAll().length
            };

            // Don't include placeholder text
            if($(this).is('[data-placeholder]')) {
                content.content = '';
            } else {
                content.content = $(this).html();
            }

            if($(this).is('[data-id]')) {
                content.id = $(this).attr('data-id');
            } else {
                contents_awaiting_id.push($(this));
            }

            // This metadata is strictly only necessary for *new* elements, but if we're trying to update
            // an element which doesn't exist, we'll create it, and then we'll need it for those elements too.
            content.column = $(this).parents('div.column').attr('data-id');
            if($(this).hasClass('html')) {
                content.type = 'html';
            } else if($(this).hasClass('title')) {
                content.type = 'title';
            } else if($(this).hasClass('lede')) {
                content.type = 'lede';
            }

            contents.push(content);
        });
        content_elements.filter(".image").each(function() {
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
                order: $(this).prevAll().length,
                content: JSON.stringify(image)
            };
            if($(this).is('[data-id]')) {
                content.id = $(this).attr('data-id');
            } else {
                contents_awaiting_id.push($(this));
            }

            // This metadata is strictly only necessary for *new* elements, but if we're trying to update
            // an element which doesn't exist, we'll create it, and then we'll need it for those elements too.
            content.column = $(this).parents('div.column').attr('data-id');
            content.type = 'image';

            contents.push(content);
        });
        content_elements.filter(".widget").each(function() {
            var content = {
                order: $(this).prevAll().length,
                content: $(this).attr('data-json')
            };

            if($(this).is('[data-id]')) {
                content.id = $(this).attr('data-id');
            } else {
                contents_awaiting_id.push($(this));
            }

            // This metadata is strictly only necessary for *new* elements, but if we're trying to update
            // an element which doesn't exist, we'll create it, and then we'll need it for those elements too.
            content.column = $(this).parents('div.column').attr('data-id');
            content.type = 'widget';

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

            // Retrieve new contents IDs
            if(result.new_content_ids.length != contents_awaiting_id.length) {
                alert("Whoops! Serveren sier at vi opprettet " + result.new_content_ids.length + " nye elementer, mens vi egentlig opprettet " + contents_awaiting_id.length + "!\n\n" +
                      "Dette er ikke bra - det kan være at du har mistet noe av arbeidet du har gjort. Du bør ta kopi av det du kan, og lagre det lokalt, før du gjør noe annet.\n\n" +
                      "Når du har tatt en lokal kopi kan du prøve å oppdatere siden, og se om noen av elementene forsvinner.\n\n" +
                      "Dette skal egentlig ikke skje. Du bør rapportere feilen til DNTs webutviklingsteam. Beklager!");
            }
            for(var i=0; i<contents_awaiting_id.length; i++) {
                contents_awaiting_id[i].attr('data-id', result.new_content_ids[i]);
            }

            // Update IDs for contents we thought existed serverside, but didn't
            for(var i=0; i<result.unexpected_content_ids.length; i++) {
                content_elements.filter("[data-id='" + result.unexpected_content_ids[i].old + "']").attr('data-id', result.unexpected_content_ids[i].new);
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
