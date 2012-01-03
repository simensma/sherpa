$(document).ready(function() {

    $(".add-dropdown .headerAdder").click(function() {
        addElement("h1", this)
    });

    function addElement(html, adder) {
        var element = $(document.createElement(html));
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
