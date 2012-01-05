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
        if(window.getSelection) {
            var selection = window.getSelection();
            var range = document.createRange();
            range.setStart($(this).get(0), start);
            range.setEnd($(this).get(0), end);
            selection.removeAllRanges();
            selection.addRange(range);
        } else if(document.selection) {
            alert("IE?");
        }
    });
};

$(document).ready(function() {
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
                $("#savearea").css('background-color', '#ffa500');
                break;

            case 'saved':
                $("#savearea #savestatus").text("Dokumentet er lagret.");
                $("#savearea #savebutton").attr('disabled', '');
                $("#savearea").css('background-color', '#00ff00');
                break;

            case 'unsaved':
                $("#savearea #savestatus").html("Dokumentet er <strong>ikke</strong> lagret.");
                $("#savearea #savebutton").removeAttr('disabled');
                $("#savearea").css('background-color', '#ff0000');
                break;
        }
    }

    $("#savearea button#savebutton").click(function() {
        if(!documentSaving) {
            documentSaving = true;
            setStatus('saving');
        } else {
            // This is a bug; the user shouldn't be able to click the button
            // while documentSaving is true. Ignore it and just disable the button.
            $("#savearea #savebutton").attr('disabled', '');
        }
    });

    function saveContent(element) {
        element.addClass('saving');
        element.children().each(function() {
            $(this).removeAttr('contentEditable');
        });
        var content = element.html();
        $.ajax({
            // Maybe this file should be rendered as a template to avoid static URLs?
            url: '/admin/ajax/save/content/' + element.attr('name') + '/',
            type: 'POST',
            data: "content=" + content
        }).done(function() {
            element.removeClass('saving');
            element.children().each(function() {
                $(this).attr('contentEditable', 'true');
            });
        });
    }
});
