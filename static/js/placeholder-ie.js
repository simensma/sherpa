$(document).ready(function() {

    /* IE doesn't support the placeholder attribute, so simulate it. */
    $("input[placeholder]").each(function() {
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
    });

});
