/* Always include CSRF-token in AJAX requests */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
    }
});

$(document).ready(function() {
    // Hide/show chosen toolbar tab
    $("#toolbar div.tab").hide().first().show();
    $("#toolbar li").click(function() {
        $("#toolbar div.tab").hide();
        $($("#toolbar div.tab")[$(this).index()]).show();
    });
    // Make toolbar draggable
    $("#toolbar").draggable();
    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');

    // Edit mode - formatting, move vertically/horizontally
    $("#cms-container").sortable({ disabled: true });
    $(".cms-row").sortable({ disabled: true });
    $("#toolbar #tabs input.formatting").click(function() {
        disableSort($("#cms-container"));
        disableSort($(".cms-row"));
        $(".cms-content").attr('contenteditable', 'true');
    });
    $("#toolbar #tabs input.vertical").click(function() {
        enableSort($("#cms-container"), 'vertical');
        disableSort($(".cms-row"));
        $(".cms-content").attr('contenteditable', 'false');
    });
    $("#toolbar #tabs input.horizontal").click(function() {
        disableSort($("#cms-container"));
        enableSort($(".cms-row"), 'horizontal');
        $(".cms-content").attr('contenteditable', 'false');
    });

    function disableSort(element) {
        element.sortable('disable');
        element.children().off('mouseenter');
        element.children().off('mouseleave');
    }

    function enableSort(element, alignment) {
        element.sortable('enable');
        element.children().on('mouseenter', function() {
            $(this).addClass('moveable ' + alignment);
        });
        element.children().on('mouseleave', function() {
            $(this).removeClass('moveable ' + alignment);
        });
    }

    // Save all content
    $("#toolbar #tabs a.save").click(function() {
        saveContent();
    });

    // Allow content editing of content elements
    $(".cms-content").attr('contenteditable', 'true');
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
