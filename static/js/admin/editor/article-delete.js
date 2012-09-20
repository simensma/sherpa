$(document).ready(function() {
    $("button.confirm-delete").click(function() {
        $(this).hide();
        $("div.final-confirm").show();
    });
});
