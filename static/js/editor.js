$.fn.setCursorAtEnd = function() {
    return this.each(function() {
        var el = $(this).contents().last();
        if(el.length > 0 && el.get(0).length) {
            el.setRange(el.get(0).length, el.get(0).length);
        }
    });
}

$.fn.setRange = function(start, end) {
    return this.each(function() {
        var selection = rangy.getSelection();
        var range = rangy.createRange();
        range.setStart($(this).get(0), start);
        range.setEnd($(this).get(0), end);
        selection.setSingleRange(range);
    });
};

$.fn.iframeDocument = function() {
    return this.get(0).contentDocument ? this.get(0).contentDocument : this.get(0).contentWindow.document;
};


$(document).ready(function() {

    // Creates an iframe with the specified content
    function createIframe(iframe, content) {
        var doc = $(iframe).iframeDocument();

        // Append the iframe content when the "loading"-document is loaded
        var intervalId = setInterval(loadOrWait, 100);
        function loadOrWait() {
            // The body tag won't have elements until it's loaded.
            if($(doc.body).length > 0) {
                clearInterval(intervalId);

                // Simulate the layout classes on html/body in the iframe
                $(doc).children().addClass($(iframe).parent().parent().attr('class'));
                $(doc.body).addClass($(iframe).parent().attr('class'));

                // Remove all temporary content and add the actual content
                $(doc.body).find("*").remove();
                $(doc.body).append(content);

                // Add event handlers for the iframe
                $(doc.body).blur(function() {
                    // Whenever an iframe loses focus, note which iframe it was
                    lastIframe = iframe;
                });
                $(doc.body).keypress(function(event) {
                    if(event.which == 8 && $(doc.body).text().length == 0) {
                        // Backspace was pressed, and there is no text content in the document
                        confirm('Todo: Confirm deletion of entire content box.');
                    }
                });
                $(doc.body).keypress(documentChange);
                $(doc.body).click(documentChange);
            }
        }

         // Create the "loading"-document, and enable designmode
         var loadingDocument = '<!DOCTYPE html><html><head><title>Editor window</title>';
         loadingDocument += '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">';
         loadingDocument += '<link rel="stylesheet" href="/static/css/layouts-formatting.css" media="screen"></head><body>';
         loadingDocument += '<h1>Laster, vennligst vent...</h1>';
         loadingDocument += '</body></html>';
         doc.open();
         doc.write(loadingDocument);
         doc.close();
         doc.designMode = 'on';
    }

    // Write content to iframes
    $("iframe").each(function() {
        // Hide the content element, which later will be appended to the iframe
        var content = $(this).prev();
        content.hide();
        createIframe(this, content.children());
        content.remove();
        // id's are consistently stored as "content-<id>", so strip "content-"
        $(this).data('id', $(this).attr('id').substring(8));
        $(this).removeAttr('id');
    });

    var lastIframe;
    var lastActiveEditElement;
    var currentActiveEditElement;

    // Note document changes upon button click
    $("#buttons button").click(function() {
        documentChange();
    });

    // Add new html-content in a specific column
    $(".add-content button.content").click(function() {
        documentChange();
        var iframe = $(document.createElement("iframe"));
        iframe.width("100%");
        iframe.height("300px");
        iframe.css('border', '1px solid #000');
        // This traversal is based on the add-content div for any layout column and may change.
        $(this).parent().parent().last().before(iframe.get(0));
        var p = document.createElement("p");
        $(p).text("Legg til innhold her...");
        createIframe(iframe.get(0), p);
    });

    $("#buttons .header").click(function() {
        lastIframe.contentDocument.execCommand('formatblock', false, 'h1');
    });

    $("#buttons .lede").click(function() {
        if(lastActiveEditElement.attr('contenteditable') === "true") {
            if(lastActiveEditElement.get(0).tagName !== "P") {
                var p = $(document.createElement("p"));
                handleEditable(p);
                p.html(lastActiveEditElement.html());
                p.addClass('lede');
                lastActiveEditElement.before(p);
                lastActiveEditElement.remove();
                p.focus();
            } else {
                lastActiveEditElement.addClass('lede');
            }
        }
    });

    $("#buttons .body").click(function() {
        lastIframe.contentDocument.execCommand('formatblock', false, 'p');
    });

    $("#buttons .bold").click(function(event) {
        lastIframe.contentDocument.execCommand('bold');
    });

    $("#buttons .italic").click(function(event) {
        lastIframe.contentDocument.execCommand('italic');
    });

    $("#buttons .underline").click(function(event) {
        lastIframe.contentDocument.execCommand('underline');
    });

    $("#buttons .ol").click(function(event) {
        lastIframe.contentDocument.execCommand('insertorderedlist');
    });

    $("#buttons .ul").click(function(event) {
        lastIframe.contentDocument.execCommand('insertunorderedlist');
    });

    $("#buttons .anchor").click(function(event) {
        lastIframe.contentDocument.execCommand('createLink', false, 'TBD');
    });

    function handleEditable(element) {
        element.attr('contenteditable', 'true');

        // Keep track of which items are currently and lastly edited
        element.focusin(function() {
            currentActiveEditElement = $(this);
        })
        element.focusout(function() {
            lastActiveEditElement = $(this);
        });

        element.keydown(function(event) {
            documentChange();
            if(event.which == 38 && element.prev().length == 1) {
                // arrow up
                element.prev().focus();
            }
            if(event.which == 40 && element.next().length == 1) {
                // arrow down
                element.next().focus();
            }
            if(event.which == 46 && element.text() == "") {
                // delete
                event.preventDefault();
                if(element.siblings().length == 0) {
                    element.parent().remove();
                } else if(element.next().length == 1) {
                    element.next().focus();
                    element.remove();
                } else if(element.prev().length == 1) {
                    element.prev().focus();
                    element.remove();
                }
            }
            if(event.which == 8 && element.text() == "") {
                // backspace
                event.preventDefault();
                if(element.siblings().length == 0) {
                    element.parent().remove();
                } else if(element.prev().length == 1) {
                    element.prev().focus();
                    element.prev().setCursorAtEnd();
                    element.remove();
                } else if(element.next().length == 1) {
                    element.next().focus();
                    element.prev().setCursorAtEnd();
                    element.remove();
                }
            }
            if(event.which == 13) {
                // enter
                event.preventDefault();
                var p = $(document.createElement("p"));
                element.after(p);
                handleEditable(p);
                p.focus();
            }
        });
    }

    /* Saving the document */

    var documentSaved = true;
    var documentSaving = false;

    function documentChange() {
        documentSaved = false;
        if(!documentSaving) {
            setStatus('unsaved');
        }
    }

    function setStatus(status) {
        switch(status) {
            case 'saving':
                $("#savearea #savestatus").text("Dokumentet lagres, vennligst vent...");
                $("#savearea #savebutton").attr('disabled', '');
                $("#savearea").css('background-color', 'rgb(255, 165, 0)');
                break;

            case 'saved':
                $("#savearea #savestatus").text("Dokumentet er lagret.");
                $("#savearea #savebutton").attr('disabled', '');
                $("#savearea").css('background-color', 'rgb(0, 128, 0)');
                break;

            case 'unsaved':
                $("#savearea #savestatus").html("Dokumentet er <strong>ikke</strong> lagret.");
                $("#savearea #savebutton").removeAttr('disabled');
                $("#savearea").css('background-color', 'rgb(255, 0, 0)');
                break;
        }
    }

    $("#savearea button#savebutton").click(function() {
        if(!documentSaving) {
            documentSaving = true;
            setStatus('saving');
            saveContent();
        } else {
            // This is a bug; the user shouldn't be able to click the button
            // while documentSaving is true. Ignore it and just disable the button.
            $("#savearea #savebutton").attr('disabled', '');
        }
    });

    function saveContent() {
        // TODO move most of this logic outside the loop!
        $("iframe").each(function() {
            // Figure out the metadata (new/existing, layout, column, order) for this content
            var iframe = this;
            var url;
            if($(this).data('id') === undefined) {
                // New content
                var layout = $(this).parents(".layout").data('id');
                var column;
                if($(this).parent(".col-one").length > 0) {
                    column = 0;
                } else if($(this).parent(".col-two").length > 0) {
                    column = 1;
                } else if($(this).parent(".col-three").length > 0) {
                    column = 2;
                }
                var order = $(this).prevAll().length + 1;
                url = '/admin/ajax/create/content/' + layout + '/' + column + '/' + order + '/';
            } else {
                // Existing content
                var id = $(this).data('id');
                url = '/admin/ajax/update/content/' + id + '/';
            }
            var data = "content=" + $($(this).iframeDocument().body).html();

            $.ajax({
                // Maybe this file should be rendered as a template to avoid static URLs?
                url: url,
                type: 'POST',
                data: data
            }).done(function(string) {
                var response = JSON.parse(string);
                $(iframe).data('id', response.id);
                documentSaved = true;
            }).fail(function(string) {
                // Todo: Fetch an error code and display corresponding message
                documentSaved = false;
            }).always(function(string) {
                documentSaving = false;
                if(documentSaved) {
                    setStatus('saved');
                } else {
                    setStatus('unsaved');
                }
            });
        });
    }

    // Store all the layout- and content-ids
    $(".layout[name]").each(function() {
        $(this).data('id', $(this).attr('name'));
        $(this).removeAttr('name');
    });
});
