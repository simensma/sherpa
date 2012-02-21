$(document).ready(function() {

    /* Include CSRF-token when applicable in AJAX requests */
    if($("input[name='csrfmiddlewaretoken']").length > 0) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
            }
        });
    }

    /* For any close button, close its parent alert */
    $("a.close").click(function() { $(this).parent().hide(); });

    /* Scale article image sidebars according to the image width */
    $("article .image-right").each(function() {
        $(this).width($(this).children("img").width());
    });

});
