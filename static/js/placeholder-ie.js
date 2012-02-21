$(document).ready(function() {

    /* IE doesn't support the placeholder attribute, so simulate it. */
    $("input[placeholder]").each(function() {
        // Note: This doesn't account for that rare case where the user actually
        // wants to input exactly what's in the placeholder.
        $(this).data('placeholder', $(this).attr('placeholder'));
        $(this).val($(this).data('placeholder'));
        $(this).removeAttr('placeholder');
        $(this).focus(function() {
            if($(this).val() == $(this).data('placeholder')) {
                $(this).val("");
            }
        });
        $(this).focusout(function() {
            if($(this).val() == "") {
                $(this).val($(this).data('placeholder'));
            }
        });
        var input = $(this);
        $(this).parents("form").submit(function() {
            if(input.val() == input.data('placeholder')) {
                input.val("");
            }
        });
    });

});
