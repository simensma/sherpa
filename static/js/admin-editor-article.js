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

    $("img.changeable").hover(function() {
        $(this).addClass('hover');
    }, function() {
        $(this).removeClass('hover');
    }).click(function() {
        $(this).removeClass('hover');
        var src = prompt("URL?");
        if(src !== null && src !== undefined) {
            $(this).attr('src', src);
        }
    });

    /* Add widget/text/image */

    function enableInsertables() {
        $("#toolbar .adders button").attr('disabled', true);
        $("#toolbar button.cancel").show();
        $(".insertable").show();
    }

    function disableInsertables() {
        $("#toolbar .adders button").removeAttr('disabled');
        $(".insertable").hide();
        $(".insertable").off('click.add');
        $("#toolbar button.cancel").hide();
    }
    $(".insertable").hide().click(disableInsertables);
    $("#toolbar button.cancel").hide().click(disableInsertables);
    $("#toolbar .adders button").click(enableInsertables);
    $("#toolbar button.add-widget").click(function() {
        $(".insertable").text("Klikk for å legge til widget her").on('click.add', function() {
            // Todo: insert widget
        });
    });
    $("#toolbar button.add-image").click(function() {
        $(".insertable").text("Klikk for å legge til bilde her").on('click.add', function() {
            // Todo: insert image
        });
    });
    $("#toolbar button.add-text").click(function() {
        $(".insertable").text("Klikk for å legge til tekst her").on('click.add', function() {
            var insertable = $(this);
            enableOverlay();
            var editable = '<div class="editable"><p></p></div>';
            $.ajax({
                url: '/sherpa/artikler/nytt-innhold/',
                type: 'POST',
                data: "column=" + encodeURIComponent(insertable.attr("data-column")) +
                      "&order=" + encodeURIComponent(insertable.attr("data-order")) +
                      "&content=" + encodeURIComponent(editable)
            }).done(function(result) {
                editable = $(editable);
                var wrapper = $('<div class="content" data-id="' + result + '"></div>').append(editable);
                var well = $('<div class="insertable well"></div>');
                insertable.after(wrapper, well);

                // Redo stuff that would happen on page load
                editable.attr('contenteditable', 'true').focus();
                well.hide();
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                disableOverlay();
            });

        });
    });

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
