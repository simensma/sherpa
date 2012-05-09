$(document).ready(function() {

    /**
     * Toolbar buttons
     */
    $("#toolbar div.formatting a.button").each(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    });
    $("#toolbar div.formatting a.button").hover(function() {
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
            var node = $(selection.anchorNode).parent();
            node.replaceWith($('<' + $(this).val() + '></' + $(this).val() + '>').prepend(node.contents()));
        });
        $("#toolbar select").val("default");
    });
    $("#toolbar a.button.anchor-add").click(function(event) {
        $("#toolbar .formatting *").hide();
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
            var url = $("#toolbar div.formatting input[name='url']").val();
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
            $("#toolbar .formatting p.anchor-insert, #toolbar .formatting div.anchor-buttons").remove();
            $("#toolbar .formatting *").show();
        }
        $("#toolbar .tab-pane.formatting").append(p, buttons);
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

    /* Show tooltip for toolbar formatting buttons */

    $("#toolbar .formatting a.button").hover(function() {
        var tooltip = $('<button class="btn btn-primary title">' + $(this).attr('data-title') + '</button>');
        tooltip.css('font-weight', 'bold');
        tooltip.css('position', 'absolute');
        tooltip.css('top', '72px');
        $(this).append(tooltip);
    }, function() {
        $("button.title").remove();
    });

});
