$(document).ready(function() {

    // Edit mode - formatting, move vertically/horizontally
    var rows = $("article");
    var columns = $("article row");
    rows.sortable({ disabled: true });
    columns.sortable({ disabled: true });
    $("#toolbar #tabs input.formatting").click(function() {
        disableSort(rows);
        disableSort(columns);
        $(".cms-content").attr('contenteditable', 'true');
    });
    $("#toolbar #tabs input.vertical").click(function() {
        enableSort(rows, 'vertical');
        disableSort(columns);
        $(".cms-content").attr('contenteditable', 'false');
    });
    $("#toolbar #tabs input.horizontal").click(function() {
        disableSort(rows);
        enableSort(columns, 'horizontal');
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

    // Allow content editing of content elements
    $(".cms-content").attr('contenteditable', 'true');

    /* Saving document */

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 30) {
            $("#toolbar p.save-text").html("<i class=\"icon-ok\"></i> Artikkelen er nylig lagret.");
        } else if(lastSaveCount < 120) {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + lastSaveCount + " sekunder siden.");
        } else {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + Math.floor(lastSaveCount / 60) + " minutter siden.");
        }

        if(lastSaveCount == 60 * 5) {
            $("div.no-save-warning").show();
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    $("#toolbar button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).hide();
        $("div.no-save-warning").hide();
        $("#toolbar p.save-text").text("Lagrer, vennligst vent...");
        enableOverlay();
        $(".cms-content").each(function(c) {
            $.ajax({
                url: '/sherpa/cms/innhold/oppdater/' + $(this).attr('data-id') + '/',
                type: 'POST',
                data: "content=" + encodeURIComponent($(this).html())
            }).done(function(result) {
                lastSaveCount = 0;
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                updateSaveCount();
                disableOverlay();
                $("#toolbar button.save").show();
            });
        });
    });

});
