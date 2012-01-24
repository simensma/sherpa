$(document).ready(function() {
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

        // Set the 'layout', 'column' and 'order'-inputfields for this widget
        var layout = $(this).parents(".layout").data('id');
        var column = $(this).parents(".column").attr('class').replace('column', '').trim().substring(4) - 1;
        var order = $(this).parents(".add-content").prevAll().length + 1;
        $("div#widgets-" + widgetType + " input[name=\"layout\"]").val(layout);
        $("div#widgets-" + widgetType + " input[name=\"column\"]").val(column);
        $("div#widgets-" + widgetType + " input[name=\"order\"]").val(order);
        $("div#widgets-" + widgetType + " form").attr('action',
          '/sherpa/artikkel/widget/opprett/quote/');

        $("div#widgets-" + widgetType).dialog('open');
    });
});
