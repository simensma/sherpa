// The idea here is that we'll create a better tagger ad hoc now, and eventually
// convert all existing use of admin/tags.js to use this tagger.

/*
    Usage:

    1. A simple tagger with manual addition/removal of tags:

    // taggerInput is a hidden jquery text-input-element in which a JSON list of tags will be filled
    TaggerAH.enable({
        targetInput: some_input
    });

    TaggerAH.addTag('some-tag');
    TaggerAH.removeTag('some-tag');
    TaggerAH.count(); // gives the tag count

    some_form.submit(function() {
        TaggerAH.collect(); // This fills the targetInput with JSON for form submission
    });


    2. Display the selected tags in a tag box

    TagDisplayAH.enable({
        targetInput: some_input,
        tagBox: some_container
    });

    If you now use TagDisplayAH.addTag and TagDisplayAH.removeTag, DOM elements will be
    added to the tag box. You can still call addTag/removeTag directly on TaggerAH to
    add tags that are NOT displayed in the tag-box, but still included on the collect call.

    Remember that you still need to call TagDisplayAH.collect() to fill the target input on
    form submission.


    3. Enable a tag-picker with typeahead

    TagDisplayAH.enable({
        targetInput: some_target_input,
        tagBox: some_container,
        pickerInput: some_picker_input
    });

    Like 2., but adds listeners to the pickerInput which automatically adds entered tags to
    TagDisplayAH. It also adds typeahead for existing tags.

 */

(function(TaggerAH, $, undefined) {
    var tags = [];
    var targetInput;

    TaggerAH.enable = function(options) {
        targetInput = options.targetInput;
    };

    TaggerAH.addTag = function(tag) {
        tag = tag.trim().toLowerCase();

        if(tag === "") {
            return {
                status: 'empty',
                cleanedTag: tag
            };
        }

        for(var j=0; j<tags.length; j++) {
            if(tags[j] == tag) {
                return {
                    status: 'exists',
                    cleanedTag: tag
                };
            }
        }

        tags.unshift(tag);
        return {
            status: 'ok',
            cleanedTag: tag
        };
    };

    TaggerAH.removeTag = function(tag) {
        for(var i=0; i<tags.length; i++) {
            if(tags[i] == tag) {
                tags.splice(i, 1);
            }
        }
    };

    TaggerAH.count = function() {
        return tags.length;
    };

    TaggerAH.collect = function() {
        targetInput.val(JSON.stringify(tags));
    };

}(window.TaggerAH = window.TaggerAH || {}, jQuery));


// TagDisplay wraps the Tagger with additional functionality for showing chosen tags
(function(TagDisplayAH, $, undefined) {

    var tagBox;
    var removeCallback;
    var pickerInput;

    TagDisplayAH.enable = function(options) {
        TaggerAH.enable(options);
        tagBox = options.tagBox;
        removeCallback = options.removeCallback;
        if(typeof options.pickerInput !== "undefined") {
            pickerInput = options.pickerInput;
            enableTagPicker();
        }

        $(document).on('click', tagBox.selector + ' div.tag a.closer', function() {
            TagDisplayAH.removeTag($(this).parent().text().trim());
            $(this).parent("div.tag").remove();
        });
    };

    TagDisplayAH.addTag = function(tag) {
        var result = TaggerAH.addTag(tag);
        if(result.status === 'ok') {
            var tagElement = $('<div class="tag"><a href="javascript:undefined" class="closer"></a> ' + result.cleanedTag + '</div>');
            tagBox.append(tagElement);
        } else if(result.status === 'exists') {
            tagBox.find("div.tag").each(function() {
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

    TagDisplayAH.removeTag = function(tag) {
        TaggerAH.removeTag(tag);
        tagBox.find("div.tag").each(function() {
            if($(this).text().trim() == tag) {
                $(this).remove();
                if(removeCallback !== undefined) {
                    removeCallback(tag);
                }
            }
        });
    };

    TagDisplayAH.count = TaggerAH.count;
    TagDisplayAH.collect = TaggerAH.collect;

    function enableTagPicker() {
        pickerInput.keyup(function(e) {
            // Add tags whenever the cursor isn't on the last word
            var typeahead = false;
            $("ul.typeahead").each(function() {
                if($(this).css('display') != 'none') {
                    typeahead = true;
                }
            });
            if(!typeahead) {
                var val = pickerInput.val();
                if(val.length > 1 && val[val.length-1] == ' ' || e.which == 13) { // Key: Enter
                    addCurrentPickerTags();
                    pickerInput.val("");
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
                addCurrentPickerTags();
                pickerInput.val("");
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
                    // Array.indexOf is JS 1.6 which IE7, IE8 doesn't support, so we'll do this the hard way
                    var exists = false;
                    for(var i=0; i<tags.length; i++) {
                        if(tags[i] == query) {
                            exists = true;
                        }
                    }
                    if(!exists) {
                        tags.unshift(query);
                    }
                    process(tags);
                });
            }
        });
    }

    function addCurrentPickerTags() {
        var tags = pickerInput.val().split(' ');
        for(var i=0; i<tags.length; i++) {
            TagDisplayAH.addTag(tags[i]);
        }
    }

}(window.TagDisplayAH = window.TagDisplayAH || {}, jQuery));
