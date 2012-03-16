$(document).ready(function() {

    $("div.dialog button.close-dialog").click(function(event) {
        event.preventDefault();
        $(this).parents("div.dialog").dialog('close');
    });

});
