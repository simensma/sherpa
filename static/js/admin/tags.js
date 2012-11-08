/* Typical use of tagger */
var TypicalTagger = function(input, tag_box) {
    return new Tagger(input, function(tag) {
        var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + tag + '</div>');
        tag_box.append(tag);
    }, function(tag) {
        tag_box.find("div.tag").each(function() {
            if($(this).text().trim().toLowerCase() == tag.toLowerCase()) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
            }
        });
    });
}

/* Core functionality */
var Tagger = function(el, newTag, existingTag) {
    var self = this;
    this.el = el;
    this.newTag = newTag;
    this.existingTag = existingTag;
    this.tags = [];
    this.autocomplete = false;

    this.el.on('change', function(e) {
        // Sorry, this is kind of ugly. 'change' is fired by both jquery and bootstrap.
        // To discriminate, we know that jquerys event won't have the 'which' property
        // (even though it is undefined).
        if(!e.hasOwnProperty('which')) {
            self.parseTags();
            self.el.val("");
        }
    });

    this.el.keyup(function(e) {
        // Add tags whenever the cursor isn't on the last word
        var typeahead = false;
        $("ul.typeahead").each(function() {
            if($(this).css('display') != 'none') {
                typeahead = true;
            }
        });
        if(!typeahead) {
            var val = self.el.val();
            if(val.length > 1 && val[val.length-1] == ' ' || e.which == 13) { // Key: Enter
                self.parseTags();
                self.el.val("");
            }
        }
    }).focusout(function(e) {
        // Add tags when losing focus, but not if typeahead is active
        var typeahead = false;
        $("ul.typeahead").each(function() {
            if($(this).css('display') != 'none') {
                typeahead = true;
            }
        });
        if(!typeahead) {
            self.parseTags();
            self.el.val("");
        }
    }).typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/tags/filter/',
                data: 'name=' + encodeURIComponent(query)
            }).done(function(result) {
                process(JSON.parse(result));
            });
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
