/**
 * Saving the document
 */

var NO_SAVE_WARNING_TIMEOUT = 60 * 5;

$(function() {

    var header = $("div.editor-header");
    var save_button = header.find("button.save");
    var no_save_warning = $("div.no-save-warning");
    var article = $("article");

    var lastSaveCount = 0;
    var updateSaveCountID;
    var statusIcon = '<i class="icon-heart"></i>';
    function updateSaveCount() {
        lastSaveCount += 1;
        save_button.html(statusIcon + ' Lagre (' + lastSaveCount + ')');

        if(lastSaveCount == NO_SAVE_WARNING_TIMEOUT) {
            no_save_warning.show();
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    save_button.click(save);
    header.find("button.preview").click(saveAndGo);
    header.find("button.save-and-quit").click(saveAndGo);
    header.find("a.quit").click(function(e) {
        if(!(confirm($(this).attr('data-confirm')))) {
            e.preventDefault();
        }
    });

    function saveAndGo() {
        var button = $(this);
        button.html('<i class="icon-search"></i> Lagrer først...');
        button.prop('disabled', true);
        var url = $(this).attr('data-href');
        save(function() {
            window.location = url;
        }, function() {
            button.html('<i class="icon-search"></i> Forhåndsvisning');
            button.prop('disabled', false);
        });
    }

    window.save = save;
    function save(done, fail) {
        if(article.find("div.crop-control").length > 0) {
            alert("Du har aktivert beskjæring av et bilde - du må gjøre deg ferdig med beskjæringen før du lagrer.");
            return;
        }

        clearTimeout(updateSaveCountID);
        save_button.prop('disabled', true);
        save_button.html('<i class="icon-heart"></i> Lagrer...');
        no_save_warning.hide();

        var data = {};

        //
        // Now iterate the client DOM and build the data structure to send to the server
        //

        // Rows
        var rows = [];
        article.children("div[data-dnt-row]").each(function() {
            var row = {
                order: $(this).prevAll().length
            };

            // Descend into columns
            row.columns = [];
            $(this).children("div.column").each(function() {
                var span;
                var offset = 0;
                $($(this).attr('class').split(' ')).each(function() {
                    if(this.startsWith('span')) {
                        span = this.substring('span'.length);
                    } else if(this.startsWith('offset')) {
                        offset = this.substring('offset'.length);
                    }
                });
                var column = {
                    span: span,
                    offset: offset,
                    order: $(this).prevAll().length
                };

                // Descend into contents
                column.contents = [];
                $(this).children("div.content").each(function() {
                    var content = {
                        order: $(this).prevAll().length
                    };

                    // Retrieve content and content type
                    if($(this).is('.html,.title,.lede')) {
                        if($(this).is('.html')) {
                            content.type = 'html';
                        } else if($(this).is('.title')) {
                            content.type = 'title';
                        } else if($(this).is('.lede')) {
                            content.type = 'lede';
                        }

                        // Don't include placeholder text
                        if($(this).is('[data-placeholder]')) {
                            content.content = '';
                        } else {
                            // Remove any editor-elements that could have been temporarily inserted as children,
                            // and supposed to be removed but remained there due to UI bugs
                            var clone = $(this).clone();
                            clone.find("div.content-control,div.tooltip").remove();

                            // And add the result
                            content.content = clone.html();
                        }
                    } else if($(this).is('.image')) {
                        content.type = 'image';
                        content.content = $(this).attr('data-json');
                    } else if($(this).is('.widget')) {
                        content.type = 'widget';
                        content.content = $(this).attr('data-json');
                    }
                    // Push the content into the column...
                    column.contents.push(content);
                });
                // The column into the row...
                row.columns.push(column);
            });
            // And the row into the rows
            rows.push(row);
        });

        // Finally add the structure+content as a JSON-string named 'rows' in data
        data.rows = JSON.stringify(rows);

        // Tags
        data.tags = JSON.stringify(TagDisplay.getTags());

        // Publish-state
        var publish = header.find("div.publish");
        data.publish_date = publish.find("input[name='date']").val();
        data.publish_time = publish.find("input[name='time']").val();
        data.status = JSON.stringify(publish.find("input[name='publish']:checked").length > 0);

        var parent_select = header.find("select[name='parent']");
        if(header.is(".page")) {
            /* Page-specific */

            // Title
            data.title = header.find("input[name='title']").val();

            // Parent page
            data.parent = parent_select.find("option:selected").val();

            // Whether or not to display ads
            data.ads = JSON.stringify(header.find("input[name='display-ads']:checked").length > 0);
        } else if(header.is(".article")) {
            /* Article-specific */

            // Authors
            var authors = [];
            $("select[name='authors'] > option:selected").each(function() {
                authors.push($(this).val());
            });
            data.authors = JSON.stringify(authors);

            // Thumbnail
            if(header.find("input[name='thumbnail'][value='none']").is(":checked")) {
                data.thumbnail = 'none';
            } else if(header.find("input[name='thumbnail'][value='default']").is(":checked")) {
                data.thumbnail = 'default';
            } else if(header.find("input[name='thumbnail'][value='new']").is(":checked")) {
                data.thumbnail = 'specified';
                data.thumbnail_url = header.find("img.article-thumbnail").attr('src');
            }
        }

        // Save content
        $.ajaxQueue({
            url: article.attr('data-dnt-save-url'),
            data: data
        }).done(function(result) {
            result = JSON.parse(result);

            lastSaveCount = 0;
            statusIcon = '<i class="icon-heart"></i>';
            save_button.removeClass('btn-danger').addClass('btn-success');
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

            // Publish-state response
            if(result.publish_error === 'unparseable_datetime') {
                alert("Publiseringstidspunktet er ikke i rett format!\n\nBruk velgeren for å velge dato, og skriv klokkeslettet som for eksempel '08:00' for å publisere kl. 8 om morgenen.\n\nSiden vi ikke vet om du ville publisere nå eller ikke, har vi satt den til 'ikke publisert'.\n\nHusk å krysse boksen bak 'Publiseres' hvis du vil publisere nå.");
                header.find("div.publish input[name='publish']").prop('checked', false);
            }

            var publish = header.find("div.publish");
            if(result.publish_error === 'auto_now') {
                publish.find("input[name='date']").val(result.publish_date);
                publish.find("input[name='time']").val(result.publish_time);
            }

            if(result.publish_error === 'error_nullify') {
                publish.find("input[name='date']").val('');
                publish.find("input[name='time']").val('');
            }

            // Thumbnail response
            if(result.thumbnail_missing_image) {
                alert("Det er ingen bilder i artikkelen å bruke som minibilde.\n\nVi har endret valget ditt til 'Ikke vis minibilde', hvis du vil ha et minibilde må du sette inn et bilde.");
                header.find("input[name='thumbnail'][value='none']").click();
            }

        }).fail(function(result) {
            statusIcon = '<i class="icon-warning-sign"></i>';
            alert("Whoops!\n\nVi klarte ikke å lagre innholdet. Er du sikker på at du har nettilgang?\n" +
                "Du kan prøve igjen til det går.\n\n" +
                "Hvis du lukker siden, vil du miste alle endringene siden sist du lagret.");
            save_button.removeClass('btn-success').addClass('btn-danger');
            if(typeof(fail) == 'function') {
                fail();
            }
        }).always(function(result) {
            updateSaveCount();
            save_button.prop('disabled', false);
        });

    }

});