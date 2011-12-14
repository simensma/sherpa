$(document).ready(function() {

    $(".editable").each(function() {
        var editelement = $(this);
        $(this).children().each(function() {
            $(this).attr('contenteditable', 'true');
            $(this).hover(function() {
                $(this).addClass('hover');
            }, function() {
                $(this).removeClass('hover');
            });
            // disable enter for headers
            if(this.nodeName == "H1") {
                $(this).keypress(function(event) {
                    // Don't make linebreaks in headers
                    if(event.which == 13) {
                        event.preventDefault();
                    }
                });
            };
            $(this).focus(function() {
                $(this).addClass('writing');
            });
            $(this).focusout(function() {
                $(this).removeClass('writing');
                saveContent(editelement);
            });
        });
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
                $(this).removeAttr('contentEditable');
            });
        });
    }

});
