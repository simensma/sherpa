$(function() {

    WidgetEditor.listen({
        widget_name: 'table',

        init: function(editor) {

            var table = editor.find("table.editor");
            var table_selector = "div.widget-editor[data-widget='table'] table.editor";
            var controls = editor.find("div.controls");
            var url_modal = $("div.modal.table-widget-url");

            // Control clicks

            $(document).on('click', table_selector + " button.delete-row", function() {
                readTable(editor);
                // Note that we're adding 1 to the index; skipping the header row which can't be removed
                var row_index = $(this).parents("tr").prevAll("tr").length + 1;
                var table_content = table.data('table_content');
                var new_table_content = [];
                table_content = table_content.slice(0, row_index).concat(table_content.slice(row_index + 1));
                table.data('table_content', table_content);
                drawTable(editor);
            });

            $(document).on('click', table_selector + " button.delete-column", function() {
                readTable(editor);
                var column_index = $(this).parent().prevAll("td.delete-column").length;
                var table_content = table.data('table_content');
                var new_table_content = [];
                for(var i = 0; i < table_content.length; i++) {
                    new_table_content[i] = table_content[i].slice(0, column_index).concat(table_content[i].slice(column_index + 1));
                }
                table.data('table_content', new_table_content);
                drawTable(editor);
            });

            $(document).on('click', table_selector + " button.add-row", function() {
                readTable(editor);
                var table_content = table.data('table_content');
                var new_row = [];
                for(var i = 0; i < table_content[0].length; i++) {
                    new_row.push({text: "Innhold"});
                }
                table_content.push(new_row);
                table.data('table_content', table_content);
                drawTable(editor);
            });

            $(document).on('click', table_selector + " button.add-column", function() {
                readTable(editor);
                var table_content = table.data('table_content');
                for(var i = 0; i < table_content.length; i++) {
                    table_content[i].push({text: "Innhold"});
                }
                table.data('table_content', table_content);
                drawTable(editor);
            });

            // Edit link
            $(document).on('click', table_selector + " a.edit-link", function() {
                var cell = $(this).parent();
                var anchor = cell.find("a.link");
                var default_link;
                if(anchor.length > 0) {
                    default_link = anchor.attr('href');
                } else {
                    default_link = 'http://';
                }
                url_modal.find("input[name='link']").val(default_link);
                table.data('edited-link', cell);
                url_modal.modal();
            });

            $(document).on('click', "div.table-widget-url button.save-link", function() {
                var cell = table.data('edited-link');
                var link = cell.find("a.link");
                var url = url_modal.find("input[name='link']").val();
                if(!url.startsWith("http://")) {
                    url = "http://" + url;
                }
                if(link.length > 0) {
                    link.attr('href', url);
                } else {
                    var span = cell.find("span.text");
                    var anchor = controls.find("a.link").clone();
                    anchor.attr('href', url);
                    anchor.text(span.text());
                    span.replaceWith(anchor);
                }
                url_modal.modal('hide');
            });

            $(document).on('click', "div.table-widget-url button.no-link", function() {
                var cell = table.data('edited-link');
                var anchor = cell.find("a.link");
                if(anchor.length > 0) {
                    var span = controls.find("span.text").clone();
                    span.text(anchor.text());
                    anchor.replaceWith(span);
                }
                // Else, this is a text element and we want a text element, so do nothing
                url_modal.modal('hide');
            });

            // Prevent all anchor clicks
            $(document).on('click', table_selector + " a.link", function(e) {
                e.preventDefault();
            });
        },

        onNew: function(editor) {
            // Set up the initial table
            var initial_table_content = [
                [
                    {text: 'Tittel 1'},
                    {text: 'Tittel 2'},
                    {text: 'Tittel 3'},
                ],
                [
                    {text: 'Innhold 1'},
                    {text: 'Innhold 2'},
                    {text: 'Innhold 3'},
                ],
            ];

            var table = editor.find("table.editor");
            table.data('table_content', initial_table_content);
            drawTable(editor);
        },

        onEdit: function(editor, widget_content) {
            editor.find("table.editor").data('table_content', widget_content.table);
            drawTable(editor);
        },

        onSave: function(editor) {
            readTable(editor);

            WidgetEditor.saveWidget({
                widget: "table",
                table: editor.find("table.editor").data('table_content'),
            });
            return true;
        }
    });

    /**
     * Reads the table editor DOM and overwrites the 'table_content' data field accordingly
     */
    function readTable(editor) {
        var table = editor.find("table.editor");
        var table_content = [[]];

        table.find("thead tr:not(.control) th:not(.control)").each(function() {
            var url;
            var text;

            if($(this).find("span").length > 0) {
                text = $(this).find("span").text();
            } else {
                url = $(this).find("a.link").attr('href');
                text = $(this).find("a.link").text();
            }

            table_content[0].push({
                url: url,
                text: text,
            });
        });

        table.find("tbody tr").each(function() {
            var row = [];

            $(this).find("td:not(.control)").each(function() {
                var url;
                var text;

                if($(this).find("span").length > 0) {
                    text = $(this).find("span").text();
                } else {
                    url = $(this).find("a.link").attr('href');
                    text = $(this).find("a.link").text();
                }

                row.push({
                    url: url,
                    text: text,
                });
            });

            table_content.push(row);
        });

        table.data('table_content', table_content);
    }

    /**
     * Clears the current table editor and draws out the DOM according to its 'table_content' data field
     */
    function drawTable(editor) {
        var i, j;
        var table = editor.find("table.editor");
        var table_content = table.data('table_content');
        var controls = editor.find("div.controls");
        var column_count = table_content[0].length;

        var item;
        var cell;
        var content;
        var row;

        // Clear out the existing table contents, if any
        table.empty();

        // Add the table header
        var thead = controls.find("thead").clone();
        var thead_upper_row = thead.find("tr.control");
        var thead_lower_row = thead.find("tr:not(.control)");
        thead.appendTo(table);

        // Add controls for each column
        $("<td></td>").appendTo(thead_upper_row);
        for(i = 0; i < column_count; i++) {
            controls.find("td.delete-column").clone().appendTo(thead_upper_row);
        }
        controls.find("td.add-column").clone().appendTo(thead_upper_row);

        // Now insert the header row (with an empty column control first)
        $('<th class="control"></th>').appendTo(thead_lower_row);
        for(i = 0; i < column_count; i++) {
            item = table_content[0][i];
            cell = $("<th></th>");
            if(item.url === undefined) {
                content = controls.find("span.text").clone();
                content.text(item.text);
                content.appendTo(cell);
            } else {
                content = controls.find("a.link").clone();
                content.attr('href', item.url);
                content.text(item.text);
                content.appendTo(cell);
            }
            cell.appendTo(thead_lower_row);
        }
        $('<th class="control"></th>').appendTo(thead_lower_row);

        // Now insert the rest of the rows
        var tbody = $("<tbody></tbody>");

        // Note that we're starting on 1 since the first row was manually inserted into thead
        for(i = 1; i < table_content.length; i++) {
            row = $("<tr></tr>");
            controls.find("td.delete-row").clone().appendTo(row);
            for(j = 0; j < table_content[i].length; j++) {
                item = table_content[i][j];
                cell = $("<td></td>");
                controls.find("a.edit-link").clone().appendTo(cell);
                if(item.url === undefined) {
                    content = controls.find("span.text").clone();
                    content.text(item.text);
                    content.appendTo(cell);
                } else {
                    content = controls.find("a.link").clone();
                    content.attr('href', item.url);
                    content.text(item.text);
                    content.appendTo(cell);
                }
                cell.appendTo(row);
            }
            $('<td class="control"></td>').appendTo(row);
            row.appendTo(tbody);
        }
        tbody.appendTo(table);

        // And finally, insert a row for the add-row control
        var tfoot = $("<tfoot></tfoot>");
        row = $("<tr class='control'></tr>");
        controls.find("td.add-row").clone().appendTo(row);
        for(i = 0; i < column_count; i++) {
            $("<td></td>").appendTo(row);
        }
        $("<td></td>").appendTo(row); // And the final control-column
        row.appendTo(tfoot);
        tfoot.appendTo(table);

    }

});
