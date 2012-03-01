$(window).load(function() {
    // Don't set contenteditable until the entire window is loaded
    $("article .editable").attr('contenteditable', 'true');
});

$(document).ready(function() {

    $(".static").hover(function() {
        $(this).addClass('static-hover');
    }, function() {
        $(this).removeClass('static-hover');
    });

    /* Saving document */

    var lastSaveCount = 0;
    var updateSaveCountID;
    function updateSaveCount() {
        lastSaveCount += 1;
        if(lastSaveCount < 30) {
            $("#toolbar p.save-text").html("<i class=\"icon-ok\"></i> Artikkelen er nylig lagret.");
        } else if(lastSaveCount < 60) {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + lastSaveCount + " sekunder siden.");
        } else {
            $("#toolbar p.save-text").html("<i class=\"icon-warning-sign\"></i> Sist lagret for " + Math.floor(lastSaveCount / 60) + " minutt" + (lastSaveCount >= 120 ? 'er' : '') + " siden.");
        }

        if(lastSaveCount == 60 * 5) {
            $("div.no-save-warning").show();
        }
        updateSaveCountID = setTimeout(updateSaveCount, 1000);
    }
    updateSaveCount();

    $("div.no-save-warning").hide();

    $("#toolbar button.save").click(function() {
        clearInterval(updateSaveCountID);
        $(this).hide();
        $("div.no-save-warning").hide();
        $("#toolbar p.save-text").text("Lagrer, vennligst vent...");
        enableOverlay();
        $("article .editable").removeAttr('contenteditable');
        var contents = [];
        $("div.content").each(function() {
            var content = {
                id: $(this).attr('data-id'),
                content: $(this).html()
            }
            contents = contents.concat([content]);
        });

        $.ajax({
            url: '/sherpa/artikler/oppdater/' + $("article").attr('data-id') + '/',
            type: 'POST',
            data: "contents=" + encodeURIComponent(JSON.stringify(contents))
        }).done(function(result) {
            lastSaveCount = 0;
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            updateSaveCount();
            disableOverlay();
            $("#toolbar button.save").show();
            $("article .editable").attr('contenteditable', 'true');
        });
    });
});

/* Figures that "span" is 8 for a class list of e.g. "offset4 span8" */
function parseColumn(classList, name) {
  for(i=0; i<classList.length; i++) {
    if(classList[i].substring(0, classList[i].length-1) == name) {
      return classList[i].substring(classList[i].length-1)
    }
  }
}
