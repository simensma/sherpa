/* Always include CSRF-token in AJAX requests */
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", $("input[name='csrfmiddlewaretoken']").val());
    }
});

/* Saving the document */

var documentSaved = true;   // True when the current document is saved
var documentSaving = false; // True when the document is currently being saved

var count = 1; // How long we've been counting since the last save
var counterId; // The interval ID

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

/* When any action that puts the document in an unsaved state is preformed, this method
 * should be called. Remember to keep it up-to-date for new actions.
 */
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
            url: '/sherpa/cms/innhold/oppdater/' + id + '/',
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

/* Deleting an iframe */
function removeIframe(iframe) {
    if(iframe.data('id') === undefined) {
        // The box was never saved, so no need to remove it from the server.
        return;
    }
    $.ajax({
        url: '/sherpa/cms/innhold/slett/' + iframe.data('id') + '/',
        type: 'POST'
    }).always(function(string) {
        // TODO: Error and success handling
    });
}

$(document).ready(function() {

    // Store all the layout- and content-ids
    $(".layout[name]").each(function() {
        $(this).data('id', $(this).attr('name'));
        $(this).removeAttr('name');
    });

    /* Attach a bunch of handlers for buttons, etc. */

    /* Clicking to save the document */
    $("#savebutton").click(attemptSave);

    /* Note that the document changed when any toolbar-button is pressed */
    $("#buttons button").click(function() {
        documentChange();
    });

    $("#buttons .header").click(function() {
        $(lastIframe).iframeDocument().execCommand('formatblock', false, 'h1');
    });

    $("#buttons .lede").click(function() {
        // Todo: Add a 'lede' class to the focused paragraph
    });

    $("#buttons .body").click(function() {
        $(lastIframe).iframeDocument().execCommand('formatblock', false, 'p');
    });

    $("#buttons .bold").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('bold');
    });

    $("#buttons .italic").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('italic');
    });

    $("#buttons .underline").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('underline');
    });

    $("#buttons .ol").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('insertorderedlist');
    });

    $("#buttons .ul").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('insertunorderedlist');
    });

    $("#buttons .anchor").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('createLink', false, 'TBD');
    });

    $("#buttons .image").click(function(event) {
        var imageURL = prompt("Angi bildeURL:", "");
        $(lastIframe).iframeDocument().execCommand('insertimage', false, imageURL);
        $($(lastIframe).iframeDocument().body).find("img").click(function() {
            if(confirm("Juster mot venstre/høyre?")) {
                $(this).css('float', 'left');
            } else {
                $(this).css('float', 'right');
            }
        });
    });

    $("#buttons .left").click(function(event) {
        var focuses = $($(lastIframe).iframeDocument().body).find(":focus");
        $(lastIframe).iframeDocument().execCommand('justifyleft');
    });

    $("#buttons .center").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('justifycenter');
    });

    $("#buttons .right").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('justifyright');
    });

    $("#buttons .full").click(function(event) {
        $(lastIframe).iframeDocument().execCommand('justifyfull');
    });
});
