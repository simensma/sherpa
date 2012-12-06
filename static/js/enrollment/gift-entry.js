$(document).ready(function() {
    $("form.gift-entry button[type='submit']").click(function() {
        $("form.gift-entry input[name='type']").val($(this).attr('data-type'));
    });
});
