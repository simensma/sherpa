$(document).ready(function() {
    $("tr.expand button").click(function() {
        var expand = $(this).parents("tr.expand");
        expand.hide();
        expand.siblings().show();
    });
});
