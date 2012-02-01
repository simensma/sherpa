$(document).ready(function() {

    // These two will be set to their respective divs when adding content
    // based on which 'add content'-button was clicked.
    var block;
    var column;

    // Store all the widget objects
    $(".widget[name]").each(function() {
        $(this).data('widget', JSON.parse($(this).attr('name')));
        $(this).removeAttr('name');
    });

    // Hide and create the widget dialogs
    var widgets = ['quote', 'promo']
    for(var i=0; i<widgets.length; i++) {
        $("div#dialog-" + widgets[i]).hide();
        $("div#dialog-" + widgets[i]).dialog({
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
        block = $(this).parents(".block");
        column = $(this).parents(".column");
        if(!documentSaved) {
            attemptSave();
        }
    });

    /* Add new content */
    $("div.add-content-dialog .content a").click(function() {
        var columnNumber = /col-(\d+)/.exec(column.attr('class'))[1] - 1;
        // Remember, 0-indexed, and two of the children are the 'edit-content' and 'add-content' divs
        var order = column.children().length - 1;
        $(this).siblings("input[name='block']").val(block.data('id'));
        $(this).siblings("input[name='column']").val(columnNumber);
        $(this).siblings("input[name='order']").val(order);
        $(this).parents("form").submit();
    });

    /* Add quote widget */
    $("div.add-content-dialog .widget a").click(function() {
        // Set input values
        var widgetType = $(this).parents(".widget").attr('class').replace('widget', '').trim();
        var columnNumber = /col-(\d+)/.exec(column.attr('class'))[1] - 1;
        // Remember, 0-indexed, and two of the children are the 'edit-content' and 'add-content' divs
        var order = column.children().length - 1;
        $("div#" + widgetType + " input[name=\"block\"]").val(block.data('id'));
        $("div#" + widgetType + " input[name=\"column\"]").val(columnNumber);
        $("div#" + widgetType + " input[name=\"order\"]").val(order);

        // Perform specific preparations for this widget
        addSpecificWidget(widgetType)

        // And open the dialog
        $("div.add-content-dialog").dialog('close');
        $("div#" + widgetType).dialog('open');
    });

    $("div.edit-widget a.edit").click(function() {
        var widget = $(this).parents(".widget").data('widget');
        var widgetType = $(this).parents(".widget").attr('class').replace('widget', '').trim();

        // Set input values
        $("div#" + widgetType + " input[name='id']").val($(this).parents(".widget").data('widget').id);

        // Perform specific preparations for this widget
        editSpecificWidget(widgetType, widget);

        // And open the dialog
        $("div#" + widgetType).dialog('open');
    });
});

function addSpecificWidget(type) {
    switch(type) {
        case 'dialog-quote':
            // Set form destination
            $("div#dialog-quote form").attr('action', '/sherpa/cms/widget/opprett/sitat/');

            // Empty the input fields, in case it was previously edited and pre-filled
            $("div#dialog-quote textarea").val("");
            $("div#dialog-quote input[name='author']").val("");

            // Set the text (header and submit button)
            $("div#dialog-quote h1").text("Legg til sitat-widget");
            $("div#dialog-quote input[type='submit']").val("Opprett sitat-widget");
          break;

        case 'dialog-promo':
            // Set form destination
            $("div#dialog-promo form").attr('action', '/sherpa/cms/widget/opprett/promo/');

            // Set the text (header and submit button)
            $("div#dialog-promo h1").text("Legg til promo-widget");
            $("div#dialog-promo input[type='submit']").val("Opprett promo-widget");
          break;
    }
}

function editSpecificWidget(type, widget) {
    switch(type) {
        case 'dialog-quote':
            // Set form destination
            $("div#dialog-quote form").attr('action', '/sherpa/cms/widget/oppdater/sitat/');

            // Set the input fields
            $("div#dialog-quote textarea").val(widget.quote);
            $("div#dialog-quote input[name='author']").val(widget.author);

            // Set the text (header and submit button)
            $("div#dialog-quote h1").text("Endre på sitat-widget");
            $("div#dialog-quote input[type='submit']").val("Oppdater sitat-widget");
          break;

        case 'dialog-promo':
            // Set form destination
            $("div#dialog-promo form").attr('action', '/sherpa/cms/widget/oppdater/promo/');

            // Set the text (header and submit button)
            $("div#dialog-promo h1").text("Endre på promo-widget");
            $("div#dialog-promo input[type='submit']").val("Oppdater promo-widget");
          break;
    }
}
