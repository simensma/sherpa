/**
 * When the document loads, move iframe contents into their respective frames,
 * set designmode on and attach applicable event handlers.
 */

// True when iframes have loaded their content and are ready to be manipulated
var iframesReady = false;

// A reference to the last iframe touched. Mostly used by buttons that should execute
// comands (e.g. bold) on the document in the last iframe.
var lastIframe;

// Creates an iframe with the specified content
function createIframe(iframe, content) {
    var doc = $(iframe).iframeDocument();

    // Append the iframe content when the "loading"-document is loaded
    var intervalId = setInterval(loadOrWait, 100);
    function loadOrWait() {
        // The body tag won't have elements until it's loaded.
        if($(doc.body).length > 0) {
            clearInterval(intervalId);

            // Simulate the block classes on html/body in the iframe
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

$(document).ready(function() {
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
});
