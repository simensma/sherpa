$(document).ready(function() {

    var form = $("form.edit-aktivitet");
    var hide_aktivitet = form.find("div.control-group.hide_aktivitet");
    var subcategories = form.find("div.control-group.subcategories");
    var subcategory_buttons = subcategories.find("div.buttons");
    var custom_subcategory = subcategories.find("input[name='custom-category']");
    var subcategory_input = subcategories.find("input[name='subcategories']");
    var association_select = form.find("select[name='association']");
    var co_association_select = form.find("select[name='co_association']");
    var images = form.find("input[name='images']");

    association_select.chosen();
    co_association_select.chosen({
        'allow_single_deselect': true
    });

    form.find("div.control-group.difficulty select[name='difficulty']").chosen();
    form.find("div.control-group.audiences select[name='audiences']").chosen();

    form.find("div.control-group.pub_date div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    });

    // Subcategories

    function toggleButtons(e) {
        // So, this is thrown when you press enter in any input element. Wtf?
        // No idea why, but pageX and pageY is zero when that happens, so avoid it.
        if(e.pageX === 0 && e.pageY === 0) {
            return $(this);
        }

        if($(this).is(".btn-danger")) {
            $(this).removeClass("btn-danger");
        } else {
            $(this).addClass("btn-danger");
        }
    }

    subcategory_buttons.find("button.subcategory").click(toggleButtons);

    // Add custom subcategories

    custom_subcategory.typeahead({
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

    custom_subcategory.keyup(function(e) {
        if(e.which == 13) { // Enter
            addCustomSubcategory();
            e.preventDefault();
        }
    });

    custom_subcategory.focusout(function() {
        addCustomSubcategory();
    });

    function addCustomSubcategory() {
        var category = custom_subcategory.val().trim();
        if(category === '') {
            return;
        }

        // Check if the tag already exists
        var exists = false;
        subcategory_buttons.find("button.subcategory").each(function() {
            if($(this).text().trim() === category) {
                $(this).addClass("btn-danger");
                exists = true;
            }
        });
        if(exists) {
            custom_subcategory.val('');
            return;
        }

        // Create the new button
        var new_button = subcategories.find("button.subcategory.fake").clone();
        new_button.text(category);
        new_button.removeClass('fake');
        subcategory_buttons.append(' ');
        subcategory_buttons.append(new_button);
        new_button.click(toggleButtons);
        new_button.show();
        custom_subcategory.val('');
    }

    // Buttons without submit-type aren't supposed to submit the form
    $(document).on('click', "button:not([type='submit'])", function(e) {
        e.preventDefault();
    });

    form.submit(function() {
        var hidden = hide_aktivitet.find("button.active").is(".hide_aktivitet");
        hide_aktivitet.find("input[name='hidden']").val(JSON.stringify(hidden));
        images.val(JSON.stringify(ImageCarouselPicker.getImages()));

        // Collect subcategory tags
        var tags = [];
        subcategory_buttons.find("button.btn-danger").each(function() {
            tags.push($(this).text());
        });
        subcategory_input.val(JSON.stringify(tags));
    });

});
