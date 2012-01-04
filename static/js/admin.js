$(document).ready(function() {

    $(".add-dropdown .header").click(function() {
        var element = $(document.createElement("h1"));
        addElement(element, this);
    });

    $(".add-dropdown .lede").click(function() {
        var element = $(document.createElement("p"));
        element.addClass('lede');
        addElement(element, this);
    });

    $(".add-dropdown .body").click(function() {
        var element = $(document.createElement("p"));
        addElement(element, this);
    });

    $(".add-dropdown .bold").click(function(event) {
        document.execCommand('bold');
    });

    $(".add-dropdown .italic").click(function(event) {
        document.execCommand('italic');
    });

    $(".add-dropdown .underline").click(function(event) {
        document.execCommand('underline');
    });

    $(".add-dropdown .anchor").click(function(event) {
        document.execCommand('createLink', false, 'TBD');
    });

    function addElement(element, adder) {
        handleEditable(element);
        $(adder).parent().parent().before(element);
        $(element).focus();
    }

    function handleEditable(element) {
        element.attr('contenteditable', 'true');
        element.keydown(function(event) {
            // Handle some keypresses
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
