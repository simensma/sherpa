/*
    Usage:

    1. A simple tagger with manual addition/removal of tags:

    // taggerInput is a hidden jquery text-input-element in which a JSON list of tags will be filled
    Tagger.enable({
        targetInput: some_input
    });

    Tagger.addTag('some-tag');
    Tagger.removeTag('some-tag');
    Tagger.count(); // gives the tag count

    some_form.submit(function() {
        Tagger.collect(); // This fills the targetInput with JSON for form submission
    });


    2. Display the selected tags in a tag box

    TagDisplay.enable({
        targetInput: some_input,
        tagBox: some_container
    });

    If you now use TagDisplay.addTag and TagDisplay.removeTag, DOM elements will be
    added to the tag box. You can still call addTag/removeTag directly on Tagger to
    add tags that are NOT displayed in the tag-box, but still included on the collect call.

    Remember that you still need to call TagDisplay.collect() to fill the target input on
    form submission.


    3. Enable a tag-picker with typeahead

    TagDisplay.enable({
        targetInput: some_target_input,
        tagBox: some_container,
        pickerInput: some_picker_input
    });

    Like 2., but adds listeners to the pickerInput which automatically adds entered tags to
    TagDisplay. It also adds typeahead for existing tags.

 */

(function(Tagger, $, undefined) {
    var tags = {};
    var targetInput = {};

    Tagger.enable = function(options) {
        var ref = typeof options.ref !== 'undefined' ? options.ref : 'default';
        tags[ref] = [];
        targetInput[ref] = options.targetInput;
    };

    Tagger.addTag = function(tag, ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';

        tag = tag.trim().toLowerCase();

        if(tag === "") {
            return {
                status: 'empty',
                cleanedTag: tag
            };
        }

        for(var j=0; j<tags[ref].length; j++) {
            if(tags[ref][j] == tag) {
                return {
                    status: 'exists',
                    cleanedTag: tag
                };
            }
        }

        tags[ref].unshift(tag);
        return {
            status: 'ok',
            cleanedTag: tag
        };
    };

    Tagger.removeTag = function(tag, ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        for(var i=0; i<tags[ref].length; i++) {
            if(tags[ref][i] == tag) {
                tags[ref].splice(i, 1);
            }
        }
    };

    Tagger.count = function(ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        return tags[ref].length;
    };

    Tagger.getTags = function(ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        return tags[ref];
    };

    Tagger.collect = function(ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        targetInput[ref].val(JSON.stringify(tags[ref]));
    };

    Tagger.reset = function(ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        tags[ref] = [];
    };

}(window.Tagger = window.Tagger || {}, jQuery));


// TagDisplay wraps the Tagger with additional functionality for showing chosen tags
(function(TagDisplay, $, undefined) {

    var tagBox = {};
    var removeCallback = {};
    var pickerInput = {};

    TagDisplay.enable = function(options) {
        var ref = typeof options.ref !== 'undefined' ? options.ref : 'default';

        Tagger.enable(options);
        tagBox[ref] = options.tagBox;
        removeCallback[ref] = options.removeCallback;
        if(typeof options.pickerInput !== "undefined") {
            pickerInput[ref] = options.pickerInput;
            enableTagPicker(ref);
        }
        addPredefinedTags(ref);

        $(document).on('click', tagBox[ref].selector + ' div.tag a.closer', function() {
            TagDisplay.removeTag($(this).parent().text().trim(), ref);
            $(this).parent("div.tag").remove();
        });
    };

    TagDisplay.addTag = function(tag, ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        var result = Tagger.addTag(tag, ref);
        if(result.status === 'ok') {
            var tagElement = $('<div class="tag"><a href="javascript:undefined" class="closer"></a> ' + result.cleanedTag + '</div>');
            tagBox[ref].append(tagElement);
        } else if(result.status === 'exists') {
            tagBox[ref].find("div.tag").each(function() {
                if($(this).text().trim() == tag) {
                    var tagElement = $(this);
                    tagElement.addClass('exists');
                    setTimeout(function() {
                        tagElement.removeClass('exists');
                    }, 1000);
                }
            });
        }
    };

    TagDisplay.removeTag = function(tag, ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';

        Tagger.removeTag(tag, ref);
        tagBox[ref].find("div.tag").each(function() {
            if($(this).text().trim() == tag) {
                $(this).remove();
                if(removeCallback[ref] !== undefined) {
                    removeCallback[ref](tag);
                }
            }
        });
    };

    TagDisplay.reset = function(ref) {
        ref = typeof ref !== 'undefined' ? ref : 'default';
        Tagger.reset(ref);
        tagBox[ref].empty();
        addPredefinedTags(ref);
    };

    TagDisplay.count = Tagger.count;
    TagDisplay.getTags = Tagger.getTags;
    TagDisplay.collect = Tagger.collect;

    function addPredefinedTags(ref) {
        if(typeof tagBox[ref].attr('data-predefined-tags') !== 'undefined' && typeof tagBox[ref].attr('data-predefined-tags') !== false) {
            var predefined = JSON.parse(tagBox[ref].attr('data-predefined-tags'));
            for(var i=0; i<predefined.length; i++) {
                TagDisplay.addTag(predefined[i], ref);
            }
        }
    }

    function enableTagPicker(ref) {
        pickerInput[ref].change(function(e) {
            // Sorry, this is kind of ugly. 'change' is fired by both jquery and bootstrap.
            // To discriminate, we know that bootstraps event doesn't have the 'which' property.
            // If you know of something better to check for here, feel free to fix this.
            if(!e.hasOwnProperty('which')) {
                addCurrentPickerTags(ref);
            }
        });
        pickerInput[ref].keyup(function(e) {
            if(e.which == 32 || (!typeaheadIsActive(ref) && e.which == 13)) { // Space, or inactive + enter
                addCurrentPickerTags(ref);
            }
        }).focusout(function(e) {
            if(!typeaheadIsActive(ref)) {
                addCurrentPickerTags(ref);
            }
        }).typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: '/tags/filter/',
                    data: { name: query }
                }).done(function(result) {
                    query = query.toLowerCase();
                    tags = JSON.parse(result);
                    // Ensure the current value is always the topmost suggestion.
                    for(var i=0; i<tags.length; i++) {
                        if(tags[i] == query) {
                            tags = tags.slice(0, i).concat(tags.slice(i + 1));
                        }
                    }
                    tags.unshift(query);
                    process(tags);
                });
            }
        });
    }

    function addCurrentPickerTags(ref) {
        var val = pickerInput[ref].val().trim();
        if(val.length === 0) {
            return;
        }
        var tags = val.split(' ');
        for(var i=0; i<tags.length; i++) {
            TagDisplay.addTag(tags[i], ref);
        }
        pickerInput[ref].val("");
    }

    function typeaheadIsActive(ref) {
        var typeahead = pickerInput[ref].siblings("ul.typeahead");
        if(typeahead.length !== 0 && typeahead.css('display') !== 'none') {
            return true;
        }
        return false;
    }

}(window.TagDisplay = window.TagDisplay || {}, jQuery));
