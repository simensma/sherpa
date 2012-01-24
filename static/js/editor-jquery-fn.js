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
