$(document).ready(function() {

    jQuery.fn.swapWith = function(to) {
        return this.each(function() {
            var copy_to = $(to).clone();
            var copy_from = $(this).clone();
            $(to).replaceWith(copy_from);
            $(this).replaceWith(copy_to);
            makeSwappable();
        });
    };

    function makeSwappable() {
    $(".swapper").click(function() {
        var l1 = $(this).parent();
        var l2 = l1.siblings($(".moveable-layout"));
        l1.swapWith(l2);
        var id1 = l1.children().first().val();
        var id2 = l2.children().first().val();
        $.ajax({
            // Maybe this file should be rendered as a template to avoid static URLs?
            url: '/admin/ajax/swap/layout/' + id1 + '/' + id2 + '/',
            type: 'POST'
        });
    });
    }

    makeSwappable();

    /*$(".moveable-layout").hover(function() {
        $(this).addClass('hover');
    }, function() {
        $(this).removeClass('hover');
    });*/

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

    // Moveable layouts
    $(".moveable-layout").draggable({
        containment: 'document'
    });

});
