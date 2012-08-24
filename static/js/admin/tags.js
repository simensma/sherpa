var Tagger = function(el, newTag, existingTag) {
    var self = this;
    this.el = el;
    this.newTag = newTag;
    this.existingTag = existingTag;
    this.tags = [];
    this.autocomplete = false;

    this.el.keydown(function(e) {
        // Add tags when user presses enter
        if(e.which == 13) {
            e.preventDefault();
            self.parseTags();
            self.el.val("");
        }
    }).keyup(function(e) {
        // Add tags on keyup (space and paste)
        var val = self.el.val();
        if(val.length > 1 && val[val.length-1] == ' ') {
            self.parseTags();
            self.el.val("");
        }
    }).focusout(function(e) {
        // Add tags when losing focus, but not if autocomplete is active
        if(!this.autocomplete) {
            self.parseTags();
            self.el.val("");
        }
    }).autocomplete({
        source: "/sherpa/bildearkiv/tag/filter/",
        open: function() { this.autocomplete = true; },
        close: function() { this.autocomplete = false; },
        select: function(event, ui) {
            event.preventDefault();
            self.el.val("");
            tags.push(ui.item.value);
        }
    });
}

Tagger.prototype.parseTags = function() {
    vals = this.el.val().split(' ');
    for(var i=0; i<vals.length; i++) {
        // Drop empty tags
        if(vals[i] == "") { continue; }

        //comma is commonly associated with seperation of tags and other stuff, they are very likely not supposed to be there
        vals[i] = vals[i].replace(/,/g, "");

        // Trim for whitespace
        vals[i] = vals[i].trim();

        // Don't add already added tags
        var cont = true;
        for(var j=0; j<this.tags.length; j++) {
            if(this.tags[j].toLowerCase() == vals[i].toLowerCase()) {
                this.existingTag(this.tags[j]);
                cont = false;
            }
        }
        if(!cont) { continue; }

        // Tag accepted
        this.tags.push(vals[i]);
        this.newTag(vals[i]);
    }
}

Tagger.prototype.removeTag = function(tag) {
    for(var i=0; i<this.tags.length; i++) {
        if(this.tags[i].toLowerCase() == tag.toLowerCase()) {
            this.tags.splice(i, 1);
        }
    }
}
