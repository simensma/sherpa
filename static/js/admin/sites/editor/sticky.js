$(function () {

    var header = $("div.editor-header");
    var sticky = header.find('.sticky');

     /* Make part of top form sticky */

    var stickyTopOffset = sticky.offset().top; // Distance from top of window to sticky on page load
    var stickyHeight = sticky.outerHeight();
    var bodyOriginalPadding = parseInt($('body').css('padding-top'), 10);
    var bodyAdjustedPadding = bodyOriginalPadding + stickyHeight;  // Body padding when sticky has position fixed

    sticky.affix({
        offset: {
            // NOTE: This has to be dynamic, should be solved by
            // making a function that returns the right value
            top: stickyTopOffset - bodyOriginalPadding
        }
    });

    sticky.on('affixed.bs.affix', function (e) {
        // When the sticky is active, add padding to body equal to sticky height
        // to avoid content from jumping up
        $('body').css('padding-top', bodyAdjustedPadding + 'px');
    });

    sticky.on('affixed-top.bs.affix', function (e) {
        $('body').css('padding-top', bodyOriginalPadding + 'px');
    });

});
