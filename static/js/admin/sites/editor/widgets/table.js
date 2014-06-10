$(function() {

    WidgetEditor.listen({
        widget_name: 'table',

        init: function(editor) {

            // Set up the initial table
            var initial_table_content = [
                [
                    {url: undefined, text: 'Tittel 1'},
                    {url: undefined, text: 'Tittel 2'},
                    {url: undefined, text: 'Tittel 3'},
                ],
                [
                    {url: undefined, text: 'Innhold 1'},
                    {url: undefined, text: 'Innhold 2'},
                    {url: undefined, text: 'Innhold 3'},
                ],
            ];

            var table = editor.find("table.editor");
            table.data('table_content', initial_table_content);
            drawTable(editor);

            var table_selector = "div.widget-editor[data-widget='table'] table.editor";

            // Control clicks
            $(document).on('click', table_selector + " button.delete-column", function() {
                var column_index = $(this).parent().prevAll("td.delete-column").length;
                var table_content = table.data('table_content');
                var new_table_content = [];
                for(var i = 0; i < table_content.length; i++) {
                    new_table_content[i] = table_content[i].slice(0, column_index).concat(table_content[i].slice(column_index + 1));
                }
                table.data('table_content', new_table_content);
                drawTable(editor);
            });

            // Prevent all anchor clicks
            $(document).on('click', table_selector + " a", function(e) {
                e.preventDefault();
            });
        },

        onEdit: function(editor, widget_content) {},

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: "table",
            });
            return true;
        }
    });

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
        for(i = 0; i < column_count; i++) {
            controls.find("td.delete-column").clone().appendTo(thead_upper_row);
        }
        controls.find("td.add-column").clone().appendTo(thead_upper_row);

        // Now insert the header row (with an empty column control first)
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
        $("<th></th>").appendTo(thead_lower_row);

        // Now insert the rest of the rows
        // Note that we're starting on 1 since the first row was manually inserted into thead
        for(i = 1; i < table_content.length; i++) {
            row = $("<tr></tr>");
            controls.find("td.delete-row").clone().appendTo(row);
            for(j = 0; j < table_content[i].length; j++) {
                item = table_content[i][j];
                cell = $("<td></td>");
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
            $("<td></td>").appendTo(row);
            row.appendTo(table);
        }

        // And finally, insert a row for the add-row control
        row = $("<tr class='control'></tr>");
        controls.find("td.add-row").clone().appendTo(row);
        for(i = 0; i < column_count; i++) {
            $("<td></td>").appendTo(row);
        }
        $("<td></td>").appendTo(row); // And the final control-column
        row.appendTo(table);

    }

});
