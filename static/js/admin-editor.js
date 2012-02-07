/* Always include CSRF-token in AJAX requests */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
    }
});

$(document).ready(function() {
    $(".block").sortable({ disabled: true });
    $("#toolbar div.tab").hide().first().show();
    $("#toolbar li").click(function() {
        $("#toolbar div.tab").hide();
        $($("#toolbar div.tab")[$(this).index()]).show();
    });

    $("#toolbar").draggable();
    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');
    $(".cms-content").attr('contenteditable', 'true');

    // Saving
    $("#toolbar #tabs a.save").click(function() {
        saveContent();
    });

});

function saveContent() {
    $(".cms-content").each(function(c) {
        $.ajax({
            url: '/sherpa/cms/innhold/oppdater/' + $(this).attr('data-id') + '/',
            type: 'POST',
            data: "content=" + encodeURIComponent($(this).html())
        }).done(function(string) {
        }).fail(function(string) {
            // Todo: Error handling
        }).always(function(string) {
        });
    });
}
