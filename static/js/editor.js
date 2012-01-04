$(document).ready(function() {
    var lastActiveEditElement;
    var currentActiveEditElement;

    // Refocus last edited element upon any button click
    $("#buttons button").click(function() {
        if(lastActiveEditElement) {
            lastActiveEditElement.focus();
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
        var element = $(document.createElement("h1"));
        addElement(element, this);
    });

    $("#buttons .lede").click(function() {
        var element = $(document.createElement("p"));
        element.addClass('lede');
        addElement(element, this);
    });

    $("#buttons .body").click(function() {
        var element = $(document.createElement("p"));
        addElement(element, this);
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

    function addElement(element, adder) {
        handleEditable(element);
        $(adder).parent().parent().before(element);
        $(element).focus();
    }

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
