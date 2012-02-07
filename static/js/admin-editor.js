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
});
