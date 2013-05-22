$(document).ready(function() {

    // All elements from the spec[1] plus header elements (h1-h6)
    // [1] http://dvcs.w3.org/hg/editing/raw-file/tip/editing.html#the-removeformat-command
    var FORMATTER_ELEMENTS = "abbr,acronym,b,bdi,bdo,big,blink,cite,code,dfn,em,font,h1,h2,h3,h4,h5,h6,i,ins,kbd,mark,nobr,q,s,samp,small,span,strike,strong,sub,sup,tt,u,var";

    var toolbar = $("#toolbar");
    var toolbarContents = toolbar.find("div.toolbar-contents")
    var anchorInsert = toolbar.find("div.anchor-insert");

    /**
     * Toolbar buttons
     */
    toolbar.find("a.button").each(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    });
    toolbar.find("a.button").hover(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    }, function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-inactive.png)');
    }).mousedown(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-active.png)');
    }).mouseup(function() {
        $(this).css('background-image', 'url(' + $(this).attr('data-image') + '-hover.png)');
    });

    toolbar.find("select.formatting").change(function() {
        var styleClass = toolbar.find("select.formatting option:selected").val();
        $(this).val("default");

        if(selection === undefined || selection.rangeCount === 0) {
            alert("Du har ikke merket noen tekst!\n\n" +
                  "Da vet jeg ikke hvilken tekst jeg skal endre skrifttype på. Klikk på teksten du vil ha endret først.");
            return $(this);
        }

        var range = selection.getRangeAt(0);
        var start = $(range.startContainer);

        if(start[0].nodeType != 3) {
            alert("Du har ikke merket et tekstelement.\n\n" +
                  "Hvis du endret teksten to ganger på rad må du huske å merke teksten igjen før du endrer den andre gang.\n\n" +
                  "Hvis markøren er på en tom linje, må du skrive litt tekst før du velger teksttype.\n\n" +
                  "Prøv 'Fjern formatering' (merk teksten igjen og klikk på malekost-ikonet til høyre)\n\n" +
                  "Hvis ikke det hjelper, bør du kanskje prøve å oppgradere eller bytte nettleser.");
            return $(this);
        }

        var container = start.parent();
        if(styleClass === 'bread') {
            if(!container.is(FORMATTER_ELEMENTS)) {
                alert("Dette elementet er allerede brødtekst.\n\n" +
                      "Hvis du mener det ikke stemmer, prøv 'Fjern formatering' (merk teksten igjen og klikk på malekost-ikonet til høyre).");
                return $(this);
            }
            mozillaMadness(container);
        } else {
            if(container.is(FORMATTER_ELEMENTS)) {
                // Replace the parent formatter element
                mozillaMadness(container, ['<span class="' + styleClass + '">', '</span>']);
            } else {
                // The element isn't contained by a formatting element. Ignore parents and mozilla madness, just wrap the contents in a span.
                start.replaceWith('<span class="' + styleClass + '">' + start.text() + '</span>');
            }
        }

        // Special cases for mozillas linebreaks. Sad fucking panda.
        function mozillaMadness(container, content) {
            if(start.prev().is("br")) {
                // Breaks are before
                start.prev().attr('data-special-case-tmp', '');
                if(start.next().is("br")) {
                    // Breaks are *both* before and after
                    start.next().attr('data-special-case-tmp-2', '');
                    var match = /(.*)<.*?data-special-case-tmp.*?>(.*)<.*?data-special-case-tmp-2.*?>(.*)/.exec(container.html());
                    var clone = container.clone().html(match[3]);
                    if(content !== undefined) {
                        match[2] = content[0] + match[2] + content[1];
                    }
                    container.html(match[1]).after('<br>', match[2], '<br>', clone);
                } else {
                    // Breaks are *only* before
                    var match = /(.*)<.*?data-special-case-tmp.*?>(.*)/.exec(container.html());
                    if(content !== undefined) {
                        match[2] = content[0] + match[2] + content[1];
                    }
                    container.html(match[1]).after('<br>', match[2]);
                }
            } else if(start.next().is("br")) {
                // Breaks are *only* after
                start.next().attr('data-special-case-tmp', '');
                var match = /(.*)<.*?data-special-case-tmp.*?>(.*)/.exec(container.html());
                if(content !== undefined) {
                    match[1] = content[0] + match[1] + content[1];
                }
                container.html(match[2]).before(match[1], '<br>');
            } else {
                // No mozilla madness, just remove the containernode <3
                var text = container.text();
                if(content !== undefined) {
                    text = content[0] + text + content[1];
                }
                container.replaceWith(text);
            }
        }

        // This refresh *might* make a second select.formatting change trigger work, even without reselecting the text.
        selection.refresh();
    });

    function addAnchor(anchorType) {
        anchorInsert.find("input[name='url']").val("");
        if(anchorType === 'url') {
            anchorInsert.find("span.url").show();
            anchorInsert.find("span.email").hide();
        } else if(anchorType === 'email') {
            anchorInsert.find("span.url").hide();
            anchorInsert.find("span.email").show();
        }
        anchorInsert.data('type', anchorType);
        toolbarContents.hide();
        anchorInsert.show();
    }

    anchorInsert.find("div.anchor-buttons button.anchor-add").click(function() {
        var range = selection.getRangeAt(0);
        // Trim the selection for whitespace (actually, just the last char, since that's most common)
        if($(range.endContainer).text().substring(range.endOffset - 1, range.endOffset) == ' ') {
            range.setEnd(range.endContainer, range.endOffset - 1);
        }
        selection.setSingleRange(range);
        var url = anchorInsert.find("input[name='url']").val().trim();
        if(url !== "") {
            if(anchorInsert.data('type') === 'url') {
                if(!url.match(/^https?:\/\//)) {
                    url = "http://" + url;
                }
            } else if(anchorInsert.data('type') === 'email') {
                if(!url.match(/^mailto:/)) {
                    url = "mailto:" + url;
                }
            }
            document.execCommand('createLink', false, url);
        }
        anchorInsert.hide();
        toolbarContents.show();
    });

    anchorInsert.find("div.anchor-buttons button.anchor-cancel").click(function() {
        anchorInsert.hide();
        toolbarContents.show();
    });

    toolbar.find("a.button.anchor-add").click(function(event) {
        addAnchor('url');
    });
    toolbar.find("a.button.email-add").click(function(event) {
        addAnchor('email');
    });
    toolbar.find("a.anchor-remove").click(function(event) {
        document.execCommand('unlink', false, null);
    });
    toolbar.find("a.button.bold").click(function(event) {
        document.execCommand('bold', false, null);
    });
    toolbar.find("a.button.italic").click(function(event) {
        document.execCommand('italic', false, null);
    });
    toolbar.find("a.button.underline").click(function(event) {
        document.execCommand('underline', false, null);
    });
    toolbar.find("a.button.ol").click(function(event) {
        document.execCommand('insertorderedlist', false, null);
    });
    toolbar.find("a.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist', false, null);
    });
    toolbar.find("a.button.align-left").click(function(event) {
        document.execCommand('justifyleft', false, null);
    });
    toolbar.find("a.button.align-center").click(function(event) {
        document.execCommand('justifycenter', false, null);
    });
    toolbar.find("a.button.align-right").click(function(event) {
        document.execCommand('justifyright', false, null);
    });
    toolbar.find("a.button.full").click(function(event) {
        document.execCommand('justifyfull', false, null);
    });
    toolbar.find("a.button.hr").click(function(event) {
        document.execCommand('inserthorizontalrule', false, null);
    });
    toolbar.find("a.button.remove-format").click(function(event) {
        document.execCommand('removeformat', false, null);

        // Also do some extra custom cleanup:

        if(selection === undefined || selection.rangeCount === 0) {
            alert("Du har ikke merket noen tekst!\n\n" +
                  "Da vet jeg ikke hvilken tekst jeg skal fjerne formatering for. Klikk på teksten du vil ha fikset først.");
            return $(this);
        }

        var ancestor = $(selection.getRangeAt(0).commonAncestorContainer);

        if(ancestor[0].nodeType === 3) {
            ancestor = ancestor.parent();
        }
        if(ancestor.is(FORMATTER_ELEMENTS)) {
            var textNode = $(document.createTextNode(ancestor.text()));
            ancestor.replaceWith(textNode);
            ancestor = textNode.parent();
        }
        ancestor.find(FORMATTER_ELEMENTS).each(function() {
            $(this).replaceWith($(this).text());
        });

        mergeTextNodes(ancestor.contents().filter(function() {
            return this.nodeType == 3;
        })[0]);

        function mergeTextNodes(textNode) {
            var text = textNode.data;
            var nodes = [textNode];
            while(textNode.nextSibling !== null && textNode.nextSibling.nodeType === 3) {
                textNode = textNode.nextSibling;
                nodes.push(textNode);
                text += textNode.data;
            }
            for(var i=1; i<nodes.length; i++) {
                $(nodes[i]).remove();
            }
            $(nodes[0]).replaceWith(text);
        }
        selection.removeAllRanges();
    });

    /* Show tooltip for toolbar formatting buttons */

    toolbar.find("a.button").hover(function() {
        var tooltip = $('<button class="btn btn-primary title">' + $(this).attr('data-title') + '</button>');
        tooltip.css('font-weight', 'bold');
        tooltip.css('position', 'absolute');
        tooltip.css('top', '36px');
        $(this).append(tooltip);
    }, function() {
        $("button.title").remove();
    });

});
