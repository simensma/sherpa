$(document).ready(function() {

    /**
     * Toolbar buttons
     */
    $("#toolbar a.button").each(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    });
    $("#toolbar a.button").hover(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    }, function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    }).mousedown(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-active.png)');
    }).mouseup(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    });

    $("#toolbar select").change(function() {
        $("select option:selected").each(function() {
            // The smart thing to do here would be:
            // document.execCommand('formatblock', false, $(this).val());
            // But IE doesn't support that, so. FML.
            if(typeof selection === "undefined") {
                alert("Jeg vet ikke hvor du vil endre skrifttypen! Du må klikke på linjen du vil gjøre til overskrift, før du velger skrifttypen her.");
                return $(this);
            }
            var node = $(selection.anchorNode);
            if(node.find(".editable").length != 0) {
                alert("Whoops, det har oppstått en liten feil! Prøv å velge teksten du vil endre skrifttypen på en gang til, og prøv igjen.");
                return $(this);
            }
            var parent = node.parent();
            while(!parent.hasClass('editable')) {
                node = parent;
                parent = node.parent();
            }
            var replacement = $('<' + $(this).val() + '></' + $(this).val() + '>');
            var clazz = $(this).attr('data-class');
            if(clazz !== undefined) {
                replacement.addClass(clazz);
            }
            if(node.get(0).nodeType == 3) {
                // Text node - wrap the text in the new node instead of replacing it
                replacement.append(node.clone());
                node.parent().prepend(replacement);
                node.remove();
            } else {
                node.replaceWith(replacement.prepend(node.contents()));
            }
        });
        $("#toolbar select").val("default");
    });
    $("#toolbar a.button.anchor-add").click(function(event) {
        $("#toolbar *").hide();
        var p = $('<p class="anchor-insert">URL-adresse: </p>');
        var input = $('<input type="text" name="url">');
        p.append(input);
        var buttons = $('<div class="anchor-buttons btn-group"><button class="btn anchor-add">Sett inn</button><button class="btn anchor-cancel">Avbryt</button></div>');
        buttons.find("button.anchor-add").click(function() {
            var range = selection.getRangeAt(0);
            // Trim the selection for whitespace (actually, just the last char, since that's most common)
            if($(range.endContainer).text().substring(range.endOffset - 1, range.endOffset) == ' ') {
                range.setEnd(range.endContainer, range.endOffset - 1);
            }
            selection.setSingleRange(range);
            var url = $("#toolbar input[name='url']").val();
            if(!url.match(/^https?:\/\//)) {
                url = "http://" + url;
            }
            document.execCommand('createLink', false, url);
            reset();
        });
        buttons.find("button.anchor-cancel").click(function() {
            reset();
        });
        function reset() {
            $("#toolbar p.anchor-insert, #toolbar .formatting div.anchor-buttons").remove();
            $("#toolbar *").show();
        }
        $("#toolbar").append(p, buttons);
    });
    $("#toolbar a.anchor-remove").click(function(event) {
        document.execCommand('unlink', false, null);
    });
    $("#toolbar a.button.bold").click(function(event) {
        document.execCommand('bold', false, null);
    });
    $("#toolbar a.button.italic").click(function(event) {
        document.execCommand('italic', false, null);
    });
    $("#toolbar a.button.underline").click(function(event) {
        document.execCommand('underline', false, null);
    });
    $("#toolbar a.button.ol").click(function(event) {
        document.execCommand('insertorderedlist', false, null);
    });
    $("#toolbar a.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist', false, null);
    });
    $("#toolbar a.button.align-left").click(function(event) {
        document.execCommand('justifyleft', false, null);
    });
    $("#toolbar a.button.align-center").click(function(event) {
        document.execCommand('justifycenter', false, null);
    });
    $("#toolbar a.button.align-right").click(function(event) {
        document.execCommand('justifyright', false, null);
    });
    $("#toolbar a.button.full").click(function(event) {
        document.execCommand('justifyfull', false, null);
    });
    $("#toolbar a.button.hr").click(function(event) {
        document.execCommand('inserthorizontalrule', false, null);
    });
    $("#toolbar a.button.remove-format").click(function(event) {
        document.execCommand('removeformat', false, null);
    });

    /* Show tooltip for toolbar formatting buttons */

    $("#toolbar a.button").hover(function() {
        var tooltip = $('<button class="btn btn-primary title">' + $(this).attr('data-title') + '</button>');
        tooltip.css('font-weight', 'bold');
        tooltip.css('position', 'absolute');
        tooltip.css('top', '36px');
        $(this).append(tooltip);
    }, function() {
        $("button.title").remove();
    });

});
