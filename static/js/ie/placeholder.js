$(document).ready(function() {

    /* IE doesn't support the placeholder attribute, so simulate it. */
    $("input[placeholder]").each(function() {
        $(this).data('placeholder', $(this).attr('placeholder'));
        $(this).removeAttr('placeholder');
        if($(this).val() == "") {
            $(this).data('holding', true); // true when the value is actually the placeholder
            $(this).val($(this).data('placeholder'));
        }
        $(this).focus(function() {
            if($(this).data('holding')) {
                $(this).data('holding', false);
                $(this).val("");
            }
        });
        $(this).focusout(function() {
            if($(this).val() == "") {
                $(this).data('holding', true);
                $(this).val($(this).data('placeholder'));
            }
        });
        var input = $(this);
        $(this).parents("form").submit(function() {
            if(input.data('holding')) {
                input.val("");
            }
        });
    });

});