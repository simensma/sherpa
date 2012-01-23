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
                        if(confirm('Vil du fjerne denne tomme innholdsboksen?')) {
                            removeIframe($(iframe));
                            $(iframe).remove();
                        }
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

    // Hide and create the widget dialogs
    var widgets = ['quote']
    for(var i=0; i<widgets.length; i++) {
        $("div#widgets-" + widgets[i]).hide();
        $("div#widgets-" + widgets[i]).dialog({
            autoOpen: false,
            modal: true
        });
    }


    $("div.add-content select").change(function() {
        if($(this).children(":selected").val().length == 0) {
            // No widget was selected
            return;
        }
        save();
        // The option value should equal the last part of the div's ID
        $("div#widgets-" + $(this).children(":selected").val()).dialog('open');
    });

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

    $("#savebutton").click(save);

    function save() {
        if(!documentSaving) {
            documentSaving = true;
            setStatus('saving');
            saveContent();
        } else {
            // This is a bug; the user shouldn't be able to click the button
            // while documentSaving is true. Ignore it and just disable the button.
            $("#savebutton").attr('disabled', '');
        }
    }

    function removeIframe(iframe) {
        if(iframe.data('id') === undefined) {
            // The box was never saved, so no need to remove it from the server.
            return;
        }
        $.ajax({
            url: '/admin/ajax/delete/content/' + iframe.data('id') + '/',
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
            var data = "content=" + encodeURIComponent($($(this).iframeDocument().body).html());

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
