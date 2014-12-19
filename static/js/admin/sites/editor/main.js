/* The main CMS editor functionality */

(function(Editor, $, undefined ) {

    var editor;
    var article;
    var insertion_templates;

    $(function() {

        editor = $("div.cms-editor");
        article = editor.find("article");
        insertion_templates = editor.find('[data-dnt-container="insertion-templates"]');

        //
        // Initialization
        //

        Editor.resetControls();

        // Prevent all anchor clicks within the article
        $(document).on('click', article.selector + ' a', function(e) {
            e.preventDefault();
        });

        // Add chosen content-type
        $(document).on(
                'click',
                article.selector +
                    ' [data-dnt-container="add-content-popover-content"] [data-dnt-container="content-item"]',
                function() {

            var add_content = $(this).parents('.popover').prev();

            // Manually hide the tooltips since mouseleave won't be triggered
            $(this).tooltip('hide');
            add_content.tooltip('hide');

            var type = $(this).attr('data-type');
            var widget_type = $(this).attr('data-widget');

            if(add_content.parents('[data-dnt-row]').length === 0) {
                // The add-content control is on a separate row without content siblings

                var prev_row = $(this).parents("div.row").prev("div[data-dnt-row]");

                var position;
                if(type !== 'columns' && prev_row.length > 0 && prev_row.children("div.column").length === 1) {
                    // The previous row exists and is a single-column; just add an element to that row
                    position = {insertion: 'append', existingElement: prev_row.children("div.column")};
                } else {
                    // Column explicitly chosen, no previous row, or not single-column; create a new row
                    var new_row = insertion_templates.find('[data-dnt-row]').clone();
                    new_row.insertAfter($(this).parents("div.row"));
                    position = {insertion: 'prepend', existingElement: new_row.find("div.column")};
                }

                if(type !== 'widget') {
                    Editor.insertContent({type: type}, position);
                } else {
                    $(document).trigger('widget.new.' + widget_type, function(widget) {
                        Editor.insertContent({type: type, widget: widget}, position);
                    });
                }
            } else {
                // The add-content control is in a column with content siblings

                var prev = add_content.prevAll("div.content").first();
                var column = $(this).parents("div.column");

                // Special rules for columns
                if(type === 'columns') {
                    var column_count = column.siblings().length + 1;
                    if(column_count > 1) {
                        alert(
                            article.attr('data-dnt-columns-into-columns-warning')
                            .replace(/%s/, column_count)
                            .replace(/\\n/g, '\n')
                        );
                        return $(this);
                    } else {
                        var following_elements = add_content.nextAll('div.content');
                        var new_row = insertion_templates.find('[data-dnt-row]').clone();
                        new_row.insertAfter($(this).parents('div.row'));
                        following_elements.detach().prependTo(new_row.find('div.column'));
                        Editor.resetControls();
                        return $(this);
                    }
                }

                var position;
                if(prev.length === 0) {
                    position = {insertion: 'prepend', existingElement: column};
                } else {
                    position = {insertion: 'after', existingElement: prev};
                }

                if(type !== 'widget') {
                    Editor.insertContent({type: type}, position);
                } else {
                    $(document).trigger('widget.new.' + widget_type, function(widget) {
                        Editor.insertContent({type: type, widget: widget}, position);
                    });
                }
            }
        });

        // Change a row's column-structure
        $(document).on('click', article.selector + ' div.edit-structure button', function() {

            // Find the first row with content elements (since the first row without may be an editor control)
            var row;
            $(this).parents("div.edit-structure").nextAll("div[data-dnt-row]").each(function() {
                if(row === undefined && $(this).find('div.content').length !== 0) {
                    row = $(this);
                }
            });

            if($(this).attr('data-type') === 'single') {
                var first_column = row.children("div.column").first();
                var extra_columns = row.children("div.column").slice(1);
                first_column.attr('class', '').addClass('column col-md-12');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(first_column);
                });
                extra_columns.remove();
            } else if($(this).attr('data-type') === 'double') {
                var first_column = row.children("div.column").first();
                var second_column = row.children("div.column").eq(1);
                var extra_columns = row.children("div.column").slice(2);

                if(second_column.length === 0) {
                    second_column = $('<div></div>');
                    second_column.insertAfter(first_column);
                }

                first_column.attr('class', '').addClass('column col-md-6');
                second_column.attr('class', '').addClass('column col-md-6');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(second_column);
                });
                extra_columns.remove();
            } else if($(this).attr('data-type') === 'sidebar-left') {
                var first_column = row.children("div.column").first();
                var second_column = row.children("div.column").eq(1);
                var extra_columns = row.children("div.column").slice(2);

                if(second_column.length === 0) {
                    second_column = $('<div></div>');
                    second_column.insertAfter(first_column);
                }

                first_column.attr('class', '').addClass('column col-md-3');
                second_column.attr('class', '').addClass('column col-md-9');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(second_column);
                });
                extra_columns.remove();
            } else if($(this).attr('data-type') === 'sidebar-right') {
                var first_column = row.children("div.column").first();
                var second_column = row.children("div.column").eq(1);
                var extra_columns = row.children("div.column").slice(2);

                if(second_column.length === 0) {
                    second_column = $('<div></div>');
                    second_column.insertAfter(first_column);
                }

                first_column.attr('class', '').addClass('column col-md-9');
                second_column.attr('class', '').addClass('column col-md-3');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(second_column);
                });
                extra_columns.remove();
            } else if($(this).attr('data-type') === 'triple') {
                var first_column = row.children("div.column").first();
                var second_column = row.children("div.column").eq(1);
                var third_column = row.children("div.column").eq(2);
                var extra_columns = row.children("div.column").slice(3);

                if(second_column.length === 0) {
                    second_column = $('<div></div>');
                    second_column.insertAfter(first_column);
                }

                if(third_column.length === 0) {
                    third_column = $('<div></div>');
                    third_column.insertAfter(second_column);
                }

                first_column.attr('class', '').addClass('column col-md-4');
                second_column.attr('class', '').addClass('column col-md-4');
                third_column.attr('class', '').addClass('column col-md-4');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(third_column);
                });
                extra_columns.remove();
            } else if($(this).attr('data-type') === 'quadruple') {
                var first_column = row.children("div.column").first();
                var second_column = row.children("div.column").eq(1);
                var third_column = row.children("div.column").eq(2);
                var fourth_column = row.children("div.column").eq(3);
                var extra_columns = row.children("div.column").slice(4);

                if(second_column.length === 0) {
                    second_column = $('<div></div>');
                    second_column.insertAfter(first_column);
                }

                if(third_column.length === 0) {
                    third_column = $('<div></div>');
                    third_column.insertAfter(second_column);
                }

                if(fourth_column.length === 0) {
                    fourth_column = $('<div></div>');
                    fourth_column.insertAfter(third_column);
                }

                first_column.attr('class', '').addClass('column col-md-3');
                second_column.attr('class', '').addClass('column col-md-3');
                third_column.attr('class', '').addClass('column col-md-3');
                fourth_column.attr('class', '').addClass('column col-md-3');

                extra_columns.each(function() {
                    $(this).children().detach().appendTo(fourth_column);
                });
                extra_columns.remove();
            }

            row.find("div.content.image").each(function() {
                if(JSON.parse($(this).attr('data-json')).crop !== undefined) {
                    ImageCropper.cropImage(
                        JSON.parse($(this).attr('data-json')).crop,
                        $(this).find('img'),
                        $(this),
                        $(this).parents('div.column').width()
                    );
                    $(this).find('img').addClass('cropped');
                }
            });
            Editor.resetControls();
        });

        // Tags, used in the header for both pages and articles
        Select2Tagger({$input: $('.editor-header input[name="tags"]')});
    });

    // Remove popovers when clicking on anything else than their trigger button
    $(document.body).on('click', function(e) {
        if(!$(e.target).is('.add-content')) {
            var editor = $("div.cms-editor");
            var article = editor.find("article");
            article.find('.add-content').popover('hide');
        }
    });

    // Enable content-item tooltips when the popover is shown, since that's when the DOM is created
    $(document.body).on('shown.bs.popover', function() {
        article.find('.popover [data-dnt-container="content-item"]').tooltip();
    });

    // Remove all editing-markup and re-build from scratch
    Editor.resetControls = function() {

        // Create a new row with a single add-content control for rows
        function cloneAddContentRow() {
            var new_row = insertion_templates.find('[data-dnt-row]').clone();
            new_row.removeAttr('data-dnt-row');

            var add_content = insertion_templates.find('div.add-content').clone();
            add_content.prependTo(new_row.find('.column'));
            return new_row;
        }

        // Remove all rows that are completely empty for content
        article.find("div[data-dnt-row]").each(function() {
            if($(this).find("div.column:has(div.content)").length === 0) {
                $(this).remove();
            }
        });

        // Remove existing editor-control markup, and leftover tooltips that for some reason haven't been removed
        article.children('div.row:not([data-dnt-row])').remove();
        article.find('div.add-content,.tooltip').remove();

        var rows = article.find("div[data-dnt-row]");
        if(rows.length === 0) {
            // Edge case; if there are *no* rows
            cloneAddContentRow().prependTo(article);
        } else {
            // Iterate existing rows
            rows.each(function() {
                var columns = $(this).find("div.column");
                var single_column = columns.length == 1;

                columns.each(function() {
                    insertion_templates.find("div.add-content").clone().prependTo($(this));
                    $(this).find("div.content").each(function() {
                        insertion_templates.find("div.add-content").clone().insertAfter($(this));
                    });
                    // If there is one great column, no nead for a trailing add-column after last content
                    if(single_column) {
                        $(this).children("div.add-content").last().remove();
                    }
                });
                insertion_templates.find("div.edit-structure").clone().insertBefore($(this));

                // If this is multiple-column, let user add single row before this row
                if(!single_column) {
                    cloneAddContentRow().insertBefore($(this));
                }
                cloneAddContentRow().insertAfter($(this));
            });
        }

        // Re-add tooltips to the new edit-structure buttons
        editor.find('.edit-structure button').tooltip();

        // Enable popovers on add-content clicks, and tooltips on the contained buttons
        var popover_content = insertion_templates.find('[data-dnt-container="add-content-popover-content"]');
        var popover_content_html = popover_content.wrap('<p>').parent().html();

        var popover_template = insertion_templates.find('[data-dnt-container="default-popover-template"]').clone();
        var row_width = article.find('[data-dnt-row]').first().width();
        popover_template.css('max-width', 'none');
        popover_template.css('width', row_width);
        var popover_template_html = popover_template.wrap('<p>').parent().html();

        article.find('.add-content').popover({
            placement: 'top',
            html: true,
            content: popover_content_html,
            template: popover_template_html,
            trigger: 'click',
        });

        article.find('.add-content').tooltip({
            placement: 'top'
        });

        $(document).on('click', '.add-content', function () {
            $(this).tooltip('hide');
        });

        $('.content.html.editable').on('paste', function (e) {
            setTimeout(function (e) {
                document.execCommand('selectAll', false, null);

                $remove_format_button = $('.toolbar.toolbar-text-formatter.text-formatter a.button.remove-format');

                if (!!$remove_format_button) {
                    $remove_format_button.click();

                } else {
                    document.execCommand('removeformat', false, null);
                }

            }.bind(this, e), 0);
        });

    };

    // Insert the specified content at the specified position
    Editor.insertContent = function(content, position) {
        function insertItem(item, position) {
            if(position.insertion === 'after') {
                item.insertAfter(position.existingElement);
            } else if(position.insertion === 'append') {
                item.appendTo(position.existingElement);
            } else if(position.insertion === 'prepend') {
                item.prependTo(position.existingElement);
            }
        }

        if(content.type === 'text' || content.type === 'columns') {
            // Note that when inserting a column, we'll insert a text element into the new column
            content = insertion_templates.find("div.content.html").clone();
            insertItem(content, position);
            content.attr('contenteditable', 'true').focus();
        } else if(content.type === 'image') {
            var image = insertion_templates.find("div.content.image").clone();
            insertItem(image, position);
            image.find("img").click();
        } else if(content.type === 'widget') {
            insertItem(content.widget, position);
        }
        Editor.resetControls();
    };

}(window.Editor = window.Editor || {}, jQuery ));
