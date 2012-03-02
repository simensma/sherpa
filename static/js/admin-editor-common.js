$(window).load(function() {
    // Don't set contenteditable until the entire window is loaded
    $("article .editable").attr('contenteditable', 'true');
});

/* Common for avanced- and article-editor */
$(document).ready(function() {

    $("div.no-save-warning").hide();
    selectableContent($(".editable"));
    changeableImages($("img.changeable"));

    /* Add widget/text/image */

    var noStructureForContentWarning = "Det er ingen rader/kolonner å sette inn innhold i! " +
        "Gå til 'struktur'-knappen først, og legg til noen rader og kolonner.";
    $("#toolbar button.cancel-content").hide().click(function() {
        $("#toolbar .adders button").removeAttr('disabled');
        $(this).hide();
        $("article .insertable").remove();
    });
    $("#toolbar button.add-widget").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        $("#toolbar .adders button").attr('disabled', true);
        $("#toolbar button.cancel-content").show();
        insertables("Klikk for å legge til widget her", $("article .column"), function() {
            // Todo: insert widget
            $("#toolbar .adders button").removeAttr('disabled');
            $("#toolbar button.cancel-content").hide();
            $("article .insertable").remove();
        });
    });
    $("#toolbar button.add-image").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        $("#toolbar .adders button").attr('disabled', true);
        $("#toolbar button.cancel-content").show();
        insertables("Klikk for å legge til bilde her", $("article .column"), function(event) {
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
            addContent($(event.target), content, 'h', done);
        });
    });
    $("#toolbar button.add-text").click(function() {
        if($("article").children().length == 0) {
            alert(noStructureForContentWarning);
            return;
        }
        $("#toolbar .adders button").attr('disabled', true);
        $("#toolbar button.cancel-content").show();
        insertables("Klikk for å legge til tekst her", $("article .column"), function(event) {
            var content = $('<div class="editable"><p><br></p></div>');
            function done() {
                selectableContent(content);
                content.attr('contenteditable', 'true').focus();
            }
            addContent($(event.target), content, 'h', done);
        });
    });

    // Hide/show chosen toolbar tab
    $("#toolbar div.tab").hide().first().show();
    $("#toolbar li").click(function() {
        $("#toolbar li").removeClass('active');
        $(this).addClass('active');
        $("#toolbar div.tab").hide();
        $($("#toolbar div.tab")[$(this).index()]).show();
    });
    // Make toolbar draggable
    $("#toolbar").draggable({
        containment: 'window'
    });
    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');

    /* Toolbar buttons */

    $("#toolbar div.button").mousedown(function() {
        $(this).toggleClass('active');
    }).mouseup(function() {
        $(this).toggleClass('active');
    }).hover(function() {
        $(this).toggleClass('hover');
    });

    $("#toolbar select").change(function() {
        $("select option:selected").each(function() {
            document.execCommand('formatblock', false, $(this).val());
        });
        $("#toolbar select").val("default");
    });
    $("#toolbar button.anchor-add").click(function(event) {
        document.execCommand('createLink', false, $("input.url").val());
    });
    $("#toolbar button.anchor-remove").click(function(event) {
        document.execCommand('unlink');
    });
    $("#toolbar div.button.body").click(function() {
        document.execCommand('formatblock', false, 'p');
    });
    $("#toolbar div.button.bold").click(function(event) {
        document.execCommand('bold');
    });
    $("#toolbar div.button.italic").click(function(event) {
        document.execCommand('italic');
    });
    $("#toolbar div.button.underline").click(function(event) {
        document.execCommand('underline');
    });
    $("#toolbar div.button.ol").click(function(event) {
        document.execCommand('insertorderedlist');
    });
    $("#toolbar div.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist');
    });
    $("#toolbar div.button.align-left").click(function(event) {
        document.execCommand('justifyleft');
    });
    $("#toolbar div.button.align-center").click(function(event) {
        document.execCommand('justifycenter');
    });
    $("#toolbar div.button.align-right").click(function(event) {
        document.execCommand('justifyright');
    });
    $("#toolbar div.button.full").click(function(event) {
        document.execCommand('justifyfull');
    });


});

function enableOverlay() {
    $("<div class=\"ui-widget-overlay\"></div>").appendTo('body');
    $("<div class=\"overlay-loader\"><h3>Lagrer, vennligst vent...</h3><p><img src=\"/static/img/ajax-loader.gif\" alt=\"Lagrer, vennligst vent...\"></p></div>")
      .appendTo('body');
}

function disableOverlay() {
    $(".ui-widget-overlay,.overlay-loader").remove();
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

/* Divs for inserting widgets/images/text */
function insertables(text, container, click) {
    var well = $('<div class="insertable well">' + text + '</div>');
    well.click(click);
    var children = container.children();
    container.prepend(well);
    children.each(function() {
        well = well.clone(true);
        $(this).after(well);
    });
}

function addContent(insertable, content, type, done) {
    enableOverlay();
    var order;
    if(insertable.prev().length > 0) {
        order = Number(insertable.prev().attr("data-order")) + 1;
    } else {
        order = 0;
    }
    $.ajax({
        url: '/sherpa/cms/innhold/ny/',
        type: 'POST',
        data: "column=" + encodeURIComponent(insertable.parent(".column").attr("data-id")) +
              "&order=" + encodeURIComponent(order) +
              "&content=" + encodeURIComponent($("<div/>").append(content).html()) +
              "&type=" + encodeURIComponent(type)
    }).done([function(result) {
        var wrapper = $('<div class="content" data-id="' + result + '" data-order="' + order +
            '"></div>').append(content);
        insertable.prev().after(wrapper);
    }, done]).fail(function(result) {
        // Todo
    }).always(function(result) {
        $("#toolbar .adders button").removeAttr('disabled');
        $("#toolbar button.cancel-content").hide();
        $("article .insertable").remove();
        disableOverlay();
    });
}
