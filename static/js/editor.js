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

    // True when iframes have loaded their content and are ready to be manipulated
    var iframesReady = false;

    // A reference to the last iframe touched. Mostly used by buttons that should execute
    // comands (e.g. bold) on the document in the last iframe.
    var lastIframe;

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
        }
    });

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
                        if(confirm('Vil du fjerne denne tomme innholdsboksen?')) {
                            removeIframe($(iframe));
                            $(iframe).remove();
                        }
                    }
                });
                $(doc.body).keypress(documentChange);
                $(doc.body).click(documentChange);
                // Todo: This will set true for the *FIRST* ready iframe, but there may be more
                // of them that are _not_ ready yet.
                iframesReady = true;
            }
        }

         // Create the "loading"-document, and enable designmode
         var loadingDocument = '<!DOCTYPE html><html><head><title>Editor window</title>';
         loadingDocument += '<meta http-equiv="Content-Type" content="text/html;charset=utf-8">';
         loadingDocument += '<link rel="stylesheet" href="/static/css/editor-formatting.css" media="screen"></head><body>';
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
    if($("iframe").length == 0) {
        // If there are no iframes, there are none to not be ready.
        iframesReady = true;
    }

    // Hide and create the widget dialogs
    var widgets = ['quote']
    for(var i=0; i<widgets.length; i++) {
        $("div#widgets-" + widgets[i]).hide();
        $("div#widgets-" + widgets[i]).dialog({
            title: "Ny widget",
            autoOpen: false,
            modal: true,
            width: "80%"
        });
    }


    $("div.add-content select").change(function() {
        if($(this).children(":selected").val().length == 0) {
            // No widget was selected
            return;
        }
        if(!documentSaved) {
            attemptSave();
        }
        // The option value should equal the last part of the div's ID
        $("div#widgets-" + $(this).children(":selected").val()).dialog('open');

        // Set the 'layout', 'column' and 'order'-inputfields for this widget
        var layout = $(this).parents(".layout").data('id');
        var column;
        var columnDiv = $(this).parents(".column");
        if(columnDiv.is($(".col-one"))) column = 0;
        if(columnDiv.is($(".col-two"))) column = 1;
        if(columnDiv.is($(".col-three"))) column = 2;
        var order = $(this).parents(".add-content").prevAll().length + 1;
        $("div#widgets-" + $(this).children(":selected").val() + " input[name=\"layout\"]").val(layout);
        $("div#widgets-" + $(this).children(":selected").val() + " input[name=\"column\"]").val(column);
        $("div#widgets-" + $(this).children(":selected").val() + " input[name=\"order\"]").val(order);
    });

    // Note document changes upon button click
    $("#buttons button").click(function() {
        documentChange();
    });

    // Add new html-content in a specific column
    $(".add-content input[type='submit']").click(function() {
        var layout = $(this).parents(".layout").data('id');
        var column;
        var columnDiv = $(this).parents(".column");
        if(columnDiv.is($(".col-one"))) column = 0;
        if(columnDiv.is($(".col-two"))) column = 1;
        if(columnDiv.is($(".col-three"))) column = 2;
        var order = $(this).parents(".add-content").prevAll().length + 1;
        $(this).siblings("input[name='layout']").val(layout);
        $(this).siblings("input[name='column']").val(column);
        $(this).siblings("input[name='order']").val(order);
    });

    $("#buttons .header").click(function() {
        lastIframe.contentDocument.execCommand('formatblock', false, 'h1');
    });

    $("#buttons .lede").click(function() {
        // Todo: Add a 'lede' class to the focused paragraph
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

    $("#buttons .image").click(function(event) {
        var imageURL = prompt("Angi bildeURL:", "");
        lastIframe.contentDocument.execCommand('insertimage', false, imageURL);
        $(lastIframe.contentDocument.body).find("img").click(function() {
            if(confirm("Juster mot venstre/høyre?")) {
                $(this).css('float', 'left');
            } else {
                $(this).css('float', 'right');
            }
        });
    });

    $("#buttons .left").click(function(event) {
        var focuses = $(lastIframe.contentDocument.body).find(":focus");
        lastIframe.contentDocument.execCommand('justifyleft');
    });

    $("#buttons .center").click(function(event) {
        lastIframe.contentDocument.execCommand('justifycenter');
    });

    $("#buttons .right").click(function(event) {
        lastIframe.contentDocument.execCommand('justifyright');
    });

    $("#buttons .full").click(function(event) {
        lastIframe.contentDocument.execCommand('justifyfull');
    });

    /* Saving the document */

    var documentSaved = true;
    var documentSaving = false;

    var count = 1;
    var counterId;

    $("#savebutton").click(attemptSave);
    function attemptSave() {
        if(!documentSaving) {
            if(!iframesReady) {
                alert('Redigeringsvinduene er ikke klare ennå! Du kan ikke lagre dokumentet før teksten er lastet, ellers kan du miste data.\n\n' +
                'Vennligst vent noen sekunder og prøv igjen. Hvis denne meldingen vedvarer, vennligst ta kontakt med webmaster.');
                return;
            }
            documentSaving = true;
            setStatus('saving');
            saveContent();
        } else {
            // This is a bug; the user shouldn't be able to click the button
            // while documentSaving is true. Ignore it and just disable the button.
            $("#savebutton").attr('disabled', '');
        }
    }

    function updateCounter() {
        $("#savebutton").text("Lagre (" + count + "s)");
        count++;
    }

    function documentChange() {
        documentSaved = false;
        if(!documentSaving) {
            setStatus('unsaved');
        }
    }

    function setStatus(status) {
        switch(status) {
            case 'saving':
                clearInterval(counterId);
                counterId = undefined;
                count = 1;
                $("#savebutton").attr('disabled', '');
                $("#savebutton").text("Lagrer...");
                $("#savebutton").css('background-color', 'rgb(255, 165, 0)');
                break;

            case 'saved':
                $("#savebutton").removeAttr('disabled');
                $("#savebutton").text("Lagret");
                $("#savebutton").css('background-color', 'rgb(0, 128, 0)');
                break;

            case 'unsaved':
                $("#savebutton").removeAttr('disabled');
                $("#savebutton").css('background-color', 'rgb(255, 0, 0)');
                if(counterId === undefined) {
                    counterId = setInterval(updateCounter, 1000);
                }
                break;
        }
    }

    function removeIframe(iframe) {
        if(iframe.data('id') === undefined) {
            // The box was never saved, so no need to remove it from the server.
            return;
        }
        $.ajax({
            url: '/sherpa/artikkel/innhold/slett/' + iframe.data('id') + '/',
            type: 'POST'
        }).always(function(string) {
            // TODO: Error and success handling
        });
    }

    function saveContent() {
        // TODO move most of this logic outside the loop!
        if($("iframe").length == 0) {
            // nothing to create or update
            setStatus('saved');
        }
        $("iframe").each(function() {
            var iframe = this;
            var id = $(this).data('id');
            var data = "content=" + encodeURIComponent($($(this).iframeDocument().body).html());
            $.ajax({
                // Maybe this file should be rendered as a template to avoid static URLs?
                url: '/sherpa/artikkel/innhold/oppdater/' + id + '/',
                type: 'POST',
                data: data
            }).done(function(string) {
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
