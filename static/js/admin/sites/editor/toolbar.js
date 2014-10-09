$(function() {

    // All elements from the spec[1] plus header elements (h1-h6)
    // [1] http://dvcs.w3.org/hg/editing/raw-file/tip/editing.html#the-removeformat-command
    var FORMATTER_ELEMENTS = "abbr,acronym,b,bdi,bdo,big,blink,cite,code,dfn,em,font,h1,h2,h3,h4,h5,h6,i,ins,kbd,mark,nobr,q,s,samp,small,span,strike,strong,sub,sup,tt,u,var";

    var toolbar = $("div.cms-editor-toolbar");
    var formatting = toolbar.find("div.formatting");

    rangy.init();

    // Make toolbar draggable, but not if input-elements are clicked
    toolbar.draggable();
    toolbar.find("input,select,button,a").mousedown(function(e) {
        e.stopPropagation();
    });

    // Draggable will set position relative, so make sure it is fixed before the user drags it
    toolbar.css('position', 'fixed');

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

    // Button-group formatting
    $(document).mouseup(function(e) {
        // Don't reset the formatting buttons if one of the buttons were clicked
        if($(e.target).parents('.formatting').length > 0) {
            return;
        }

        var selection = rangy.getSelection();
        formatting.find('button').prop('disabled', false).removeClass('active');

        // No selection or range?
        if(selection === undefined || selection.rangeCount === 0) {
            formatting.find('button').prop('disabled', true);
            return;
        }

        // Look up the containing element
        var container = $(selection.getRangeAt(0).startContainer).parent();

        // Ensure it's within an editable
        if(!container.is('.editable') && container.parents('.editable').length === 0) {
            formatting.find('button').prop('disabled', true);
            return;
        }

        // If this is an anchor, the styled container will be its parent
        if(container.is('a')) {
            container = container.parent();
        }

        // Now figure out what kind of styling it has, and mark the appropriate button as active
        if(container.is('h1') || container.hasClass('h1')) {
            formatting.find('button[data-format="h1"]').addClass('active');
        } else if(container.is('h2') || container.hasClass('h2')) {
            formatting.find('button[data-format="h2"]').addClass('active');
        } else if(container.is('h3') || container.hasClass('h3')) {
            formatting.find('button[data-format="h3"]').addClass('active');
        } else if(container.hasClass('lede')) {
            formatting.find('button[data-format="lede"]').addClass('active');
        } else if(container.is('div') || container.is('p')) {
            formatting.find('button[data-format="bread"]').addClass('active');
        }
    });

    formatting.find("button").click(function() {
        function resetSelection(text_node) {
            // After the DOM has been manipulated, call this with the new text node which was changed to reselect it
            setTimeout(function() {
                var selection = rangy.getSelection();
                var range = rangy.createRange();
                range.selectNodeContents(text_node);
                selection.setSingleRange(range);
                selection.refresh();
            }, 0);
        }

        var styleClass = $(this).attr('data-format');
        formatting.find("button").removeClass('active');
        $(this).addClass('active');

        var selection = rangy.getSelection();
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
                return $(this);
            }
            mozillaMadness(container);
        } else {
            if(container.is(FORMATTER_ELEMENTS)) {
                // Replace the parent formatter element
                mozillaMadness(container, ['<span class="' + styleClass + '">', '</span>']);
            } else {
                // The element isn't contained by a formatting element. Ignore parents and mozilla madness, just wrap the contents in a span.
                var replacement = $('<span class="' + styleClass + '">' + start.text() + '</span>');
                start.replaceWith(replacement);
                resetSelection(replacement.contents().get(0));
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
                    resetSelection(container.contents().get(0));
                } else {
                    // Breaks are *only* before
                    var match = /(.*)<.*?data-special-case-tmp.*?>(.*)/.exec(container.html());
                    if(content !== undefined) {
                        match[2] = content[0] + match[2] + content[1];
                    }
                    container.html(match[1]).after('<br>', match[2]);
                    resetSelection(container.contents().get(0));
                }
            } else if(start.next().is("br")) {
                // Breaks are *only* after
                start.next().attr('data-special-case-tmp', '');
                var match = /(.*)<.*?data-special-case-tmp.*?>(.*)/.exec(container.html());
                if(content !== undefined) {
                    match[1] = content[0] + match[1] + content[1];
                }
                container.html(match[2]).before(match[1], '<br>');
                resetSelection(container.contents().get(0));
            } else {
                // No mozilla madness, just remove the containernode <3
                var wrapper;
                var text_element;
                if(content !== undefined) {
                    wrapper = $(content[0] + content[1]);
                    text_element = container.contents().get(0);
                    wrapper.append(text_element);
                } else {
                    wrapper = container.contents();
                    text_element = wrapper.get(0);
                }
                container.replaceWith(wrapper);
                resetSelection(text_element);
            }
        }
    });

    toolbar.find("a.button.anchor-add").click(function(event) {
        var selection = rangy.getSelection();

        if(selection === undefined || selection.rangeCount === 0) {
            // No selection or ranges - ignore the anchor button click
            return;
        }

        var range = selection.getRangeAt(0);
        var ancestor = $(range.commonAncestorContainer).parent();

        if(ancestor.parents('.editable').length === 0 && !ancestor.is('.editable')) {
            // User hasn't selected text in an editable element - ignore the anchor button click
            return;
        }

        var existing_url;
        if(ancestor.is('a')) {
            existing_url = ancestor.attr('href');

            // Make sure the entire anchor is included in the range
            range.setStartBefore(range.startContainer);
            range.setEndAfter(range.startContainer);
        }
        UrlPicker.open({
            existing_url: existing_url,
            done: function(result) {
                // Trim the selection for whitespace (actually, just the last char, since that's most common)
                if($(range.endContainer).text().substring(range.endOffset - 1, range.endOffset) == ' ') {
                    range.setEnd(range.endContainer, range.endOffset - 1);
                }
                selection.setSingleRange(range);
                document.execCommand('createLink', false, result.url);
            },
        });
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
        var selection = rangy.getSelection();
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

});
