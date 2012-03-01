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

    selectableContent($(".editable"));
    changeableImages($("img.changeable"));

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
            // Show the insertable to get its width (it'll get hidden by disableInsertables() first)
            var width = $(this).show().width();
            $(this).hide();
            var image = $('<img class="changeable" src="/static/img/article/placeholder-bottom.png" alt="placeholder">');
            var br = $('<br>');
            var editable = $('<div class="editable">BILDETEKST: Donec ut libero sed arcu vehicula.<br><em>Foto: Kari Nordmann/DNT</em></div>');
            var content = $("<div/>").append(image, br, editable);
            function done() {
                selectableContent(editable);
                changeableImages(image);
                editable.attr('contenteditable', 'true');
                // We don't want the default overlay to be there when we pick a new picture.
                // It will be disabled when the ajax 'always' callback is called, but that's
                // after this callback is done, so we'll just disable it twice.
                disableOverlay();
                image.click();
            }
            addContent($(this), content, 'h', done);
        });
    });
    $("#toolbar button.add-text").click(function() {
        $(".insertable").text("Klikk for å legge til tekst her").on('click.add', function() {
            var content = $('<div class="editable"><p><br></p></div>');
            function done() {
                selectableContent(content);
                content.attr('contenteditable', 'true').focus();
            }
            addContent($(this), content, 'h', done);
        });
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

/* Adds event listeners to images for changing the image */
function changeableImages(images) {
    images.hover(function() {
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
}

/* Adds event listeners to selected content for highlighting it */
function selectableContent(content) {
    content.click(function() {
        $(this).addClass('selected');
    }).focusout(function() {
        $(this).removeClass('selected');
    });
}

function addContent(insertable, content, type, done) {
    enableOverlay();
    $.ajax({
        url: '/sherpa/artikler/nytt-innhold/',
        type: 'POST',
        data: "column=" + encodeURIComponent(insertable.attr("data-column")) +
              "&order=" + encodeURIComponent(insertable.attr("data-order")) +
              "&content=" + encodeURIComponent($("<div/>").append(content).html()) +
              "&type=" + encodeURIComponent(type)
    }).done([function(result) {
        var wrapper = $('<div class="content" data-id="' + result + '"></div>').append(content);
        var well = $('<div class="insertable well" data-column="' +
            insertable.attr("data-column") + '" data-order="' +
            (Number(insertable.attr("data-order")) + 1) + '"></div>');
        insertable.after(wrapper, well);
        well.hide();
    }, done]).fail(function(result) {
        // Todo
    }).always(function(result) {
        disableOverlay();
    });
}