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

$(document).ready(function() {

    // Write content to iframes
    $("iframe").each(function() {
        var doc = this.contentDocument;
        doc.open();
        doc.designMode = 'on';
        doc.write('<!DOCTYPE html><head><title>Editor window</title></head><body>');
        doc.write($(this).html());
        doc.write('</body></html>');
        doc.close();
    });

    var lastActiveEditElement;
    var currentActiveEditElement;

    // Refocus last edited element upon any button click
    $("#buttons button").click(function() {
        documentChange();
        if(lastActiveEditElement) {
            setTimeout(function() { lastActiveEditElement.focus() }, 20);
        }
    });

    $(".add-content button.content").click(function() {
        documentChange();
        var element = $(document.createElement("div"));
        element.addClass('htmlcontent');
        var p = $(document.createElement("p"));
        element.append(p);
        handleEditable(p);
        $(this).parent().parent().before(element);
        p.focus();
    });

    $("#buttons .header").click(function() {
        if(lastActiveEditElement) {
            var h1 = $(document.createElement("h1"));
            h1.html(lastActiveEditElement.html());
            handleEditable(h1);
            lastActiveEditElement.before(h1);
            lastActiveEditElement.remove();
            h1.focus();
        }
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
        if(lastActiveEditElement.attr('contenteditable') === "true") {
            if(lastActiveEditElement.get(0).tagName !== "P") {
                var p = $(document.createElement("p"));
                handleEditable(p);
                p.html(lastActiveEditElement.html());
                lastActiveEditElement.before(p);
                lastActiveEditElement.remove();
                p.focus();
            } else {
                lastActiveEditElement.removeClass('lede');
            }
        }
    });

    $("#buttons .bold").click(function(event) {
        document.execCommand('bold');
    });

    $("#buttons .italic").click(function(event) {
        document.execCommand('italic');
    });

    $("#buttons .underline").click(function(event) {
        document.execCommand('underline');
    });

    $("#buttons .anchor").click(function(event) {
        document.execCommand('createLink', false, 'TBD');
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
        $("div.htmlcontent").each(function() {
            var children = $(this).children();
            children.removeAttr('contenteditable');
            var id = $(this).data('id');
            var url;
            var data;
            if(id) {
                url = '/admin/ajax/update/content/' + $(this).data('id') + '/';
                data = "content=" + $(this).html()
            } else {
                var layout = $(this).parents(".layout").data('id');
                var column;
                if($(this).parents(".full, .left, .main-column").length > 0) {
                    column = 0;
                } else if($(this).parents(".middle, .column-of-2.right, aside").length > 0) {
                    column = 1;
                } else if($(this).parents(".column-of-3.right").length > 0) {
                    column = 2;
                }
                var pa = $(this).prevAll();
                var order = $(this).prevAll().length + 1;
                url = '/admin/ajax/create/content/' + layout + '/' + column + '/' + order + '/';
                data = "content=" + $(this).html()
            }
            $.ajax({
                // Maybe this file should be rendered as a template to avoid static URLs?
                url: url,
                type: 'POST',
                data: data
            }).done(function() {
                documentSaved = true;
            }).fail(function() {
                // Todo: Fetch an error code and display corresponding message
                documentSaved = false;
            }).always(function() {
                children.attr('contenteditable', 'true');
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
    $(".layout[name], .htmlcontent[name]").each(function() {
        $(this).data('id', $(this).attr('name'));
        $(this).removeAttr('name');
    });

    // Handle all newly created content-elements
    $(".htmlcontent").children().each(function() {
        handleEditable($(this));
    });
});
