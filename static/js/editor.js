$(document).ready(function() {
    var lastActiveEditElement;
    var currentActiveEditElement;

    // Refocus last edited element upon any button click
    $("#buttons button").click(function() {
        if(lastActiveEditElement) {
            setTimeout(function() { lastActiveEditElement.focus() }, 20);
        }
    });

    $(".add-content button.content").click(function() {
        var element = $(document.createElement("div"));
        element.addClass('htmlcontent');
        var p = $(document.createElement("p"));
        element.append(p);
        handleEditable(p);
        $(this).parent().parent().before(element);
        p.focus();
    });

    $("#buttons .header").click(function() {
        if(lastActiveEditElement.attr('contenteditable') === "true") {
            var h1 = $(document.createElement("h1"));
            h1.html(lastActiveEditElement.html());
            handleEditable(h1);
            lastActiveEditElement.before(h1);
            lastActiveEditElement.remove();
            h1.focus();
        } else {
            alert('fail, du må ha musa på rett plass');
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
                element.remove();
            }
            if(event.which == 8 && element.text() == "") {
                // backspace
                event.preventDefault();
                if(element.prev().length == 1) {
                    element.prev().focus();
                    var len = element.prev().text().length;
                    element.prev().setCursorLast();
                }
                element.remove();
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
