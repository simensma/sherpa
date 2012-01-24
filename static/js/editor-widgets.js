$(document).ready(function() {

    // These two will be set to their respective divs when adding content
    // based on which 'add content'-button was clicked.
    var layout;
    var column;

    // Store all the widget objects
    $(".widget[name]").each(function() {
        $(this).data('widget', JSON.parse($(this).attr('name')));
        $(this).removeAttr('name');
    });

    // Hide and create the widget dialogs
    var widgets = ['quote']
    for(var i=0; i<widgets.length; i++) {
        $("div#widgets-" + widgets[i]).hide();
        $("div#widgets-" + widgets[i]).dialog({
            title: "Ny widget",
            autoOpen: false,
            modal: true,
            width: "80%"
        });
    }

    // Hide and create the add-content dialog
    $("div.add-content-dialog").hide();
    $("div.add-content-dialog").dialog({
        title: "Legg til innhold",
        autoOpen: false,
        modal: true,
        width: "80%"
    });

    /* Adding new content or widgets */
    $("div.add-content a img").click(function() {
        $("div.add-content-dialog").dialog('open');
        layout = $(this).parents(".layout");
        column = $(this).parents(".column");
        if(!documentSaved) {
            attemptSave();
        }
    });

    /* Add new content */
    $("div.add-content-dialog .content a").click(function() {
        var columnNumber = column.attr('class').replace('column', '').trim().substring(4) - 1;
        var order = column.children().length; // Remember, one of the children is the 'add-content' div
        $(this).siblings("input[name='layout']").val(layout.data('id'));
        $(this).siblings("input[name='column']").val(columnNumber);
        $(this).siblings("input[name='order']").val(order);
        $(this).parents("form").submit();
    });

    /* Add quote widget */
    $("div.add-content-dialog .widget-quote a").click(function() {
        // Set form destination and input values
        $("div#widgets-quote form").attr('action',
          '/sherpa/artikkel/widget/opprett/sitat/');
        var columnNumber = column.attr('class').replace('column', '').trim().substring(4) - 1;
        var order = column.children().length; // Remember, one of the children is the 'add-content' div
        $("div#widgets-quote input[name=\"layout\"]").val(layout.data('id'));
        $("div#widgets-quote input[name=\"column\"]").val(columnNumber);
        $("div#widgets-quote input[name=\"order\"]").val(order);

        // Empty the input fields, in case it was previously edited and pre-filled
        $("div#widgets-quote textarea").val("");
        $("div#widgets-quote input[name='author']").val("");

        // Set the text (header and submit button)
        $("div#widgets-quote h1").text("Legg til sitat-widget");
        $("div#widgets-quote input[type='submit']").val("Opprett sitat-widget");

        // And open the dialog
        $("div.add-content-dialog").dialog('close');
        $("div#widgets-quote").dialog('open');
    });

    $("div.edit-widget a.edit").click(function() {
        var widget = $(this).parents(".widget").data('widget');
        var widgetType = $(this).parents(".widget").attr('class').replace('widget', '').trim();

        // Set form destination and input values
        $("div#widgets-" + widgetType + " form").attr('action',
          '/sherpa/artikkel/widget/oppdater/sitat/');
        $("div#widgets-" + widgetType + " input[name='id']").val($(this).parents(".widget").data('widget').id);

        // Set the input fields
        // Todo: This doesn't make sense, widgetType is dynamic but we're
        // specifically setting quote widget data.
        $("div#widgets-" + widgetType + " textarea").val(widget.quote);
        $("div#widgets-" + widgetType + " input[name='author']").val(widget.author);

        // Set the text (header and submit button)
        $("div#widgets-" + widgetType + " h1").text("Endre på sitat-widget");
        $("div#widgets-" + widgetType + " input[type='submit']").val("Oppdater sitat-widget");

        // And open the dialog
        $("div#widgets-" + widgetType).dialog('open');
    });
});
