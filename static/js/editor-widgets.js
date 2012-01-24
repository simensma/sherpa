$(document).ready(function() {
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

    $("div.add-content select").change(function() {
        if($(this).children(":selected").val().length == 0) {
            // No widget was selected
            return;
        }
        if(!documentSaved) {
            attemptSave();
        }

        // The option value should equal the last part of the div's ID
        var widgetType = $(this).children(":selected").val();

        // Set form destination and input values
        $("div#widgets-" + widgetType + " form").attr('action',
          '/sherpa/artikkel/widget/opprett/sitat/');
        var layout = $(this).parents(".layout").data('id');
        var column = $(this).parents(".column").attr('class').replace('column', '').trim().substring(4) - 1;
        var order = $(this).parents(".add-content").prevAll().length + 1;
        $("div#widgets-" + widgetType + " input[name=\"layout\"]").val(layout);
        $("div#widgets-" + widgetType + " input[name=\"column\"]").val(column);
        $("div#widgets-" + widgetType + " input[name=\"order\"]").val(order);

        // Empty the input fields, in case it was previously edited and pre-filled
        $("div#widgets-" + widgetType + " textarea").val(widget.quote);
        $("div#widgets-" + widgetType + " input[name='author']").val(widget.author);

        // Set the text (header and submit button)
        $("div#widgets-" + widgetType + " h1").text("Legg til sitat-widget");
        $("div#widgets-" + widgetType + " input[type='submit']").val("Opprett sitat-widget");

        // And open the dialog
        $("div#widgets-" + widgetType).dialog('open');
    });

    $("div.edit-widget a.edit").click(function() {
        var widget = $(this).parents(".widget").data('widget');
        var widgetType = $(this).parents(".widget").attr('class').replace('widget', '').trim();

        // Set form destination and input values
        $("div#widgets-" + widgetType + " form").attr('action',
          '/sherpa/artikkel/widget/oppdater/sitat/');
        $("div#widgets-" + widgetType + " input[name='id']").val($(this).parents(".widget").data('widget').id);

        // Set the input fields
        $("div#widgets-" + widgetType + " textarea").val(widget.quote);
        $("div#widgets-" + widgetType + " input[name='author']").val(widget.author);

        // Set the text (header and submit button)
        $("div#widgets-" + widgetType + " h1").text("Endre på sitat-widget");
        $("div#widgets-" + widgetType + " input[type='submit']").val("Oppdater sitat-widget");

        // And open the dialog
        $("div#widgets-" + widgetType).dialog('open');
    });
});
