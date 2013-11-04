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

    // Dates
    var dates = form.find("div.section.dates");
    var dates_input = dates.find("input[name='dates']");
    var dates_to_delete_input = dates.find("input[name='dates_to_delete']");
    var existing_dates = dates.find("div.date-root:not(.hide)");
    var add_date_button = dates.find("button.add-date");

    var date_views = [];
    var date_radio_counter = 0;
    var date_ids_to_delete = [];

    existing_dates.each(function() {
        date_views.push(new AktiviteterDatesView({
            root: $(this)
        }));
    });

    add_date_button.click(function() {
        var hidden_root = dates.find("div.date-root.hide");
        var new_root = hidden_root.clone();
        // Cloning with events doesn't work for popover, so reactivate any popovers.
        new_root.find("*[data-popover]").popover({
            container: 'body'
        });

        // All radio button groups need unique names, so generate names with a counter.
        new_root.find("input[name='enrollment']").attr('name', 'enrollment-' + date_radio_counter);
        new_root.find("input[name='contact_type']").attr('name', 'contact_type-' + date_radio_counter);
        date_radio_counter += 1;

        new_root.removeClass('hide');
        new_root.hide(); // Hide it even though we don't want the 'hide' class on it.
        date_views.push(new AktiviteterDatesView({
            root: new_root
        }));
        new_root.insertBefore(hidden_root);
        new_root.slideDown();
    });

    $(document).on('click', dates.selector + ' a.delete-date', function() {
        // Ugh, remove the array element manually
        var root = $(this).parents("div.date-root");
        var new_date_views = [];
        for(var i=0; i<date_views.length; i++) {
            if(date_views[i].root[0] !== root[0]) {
                new_date_views.push(date_views[i]);
            }
        }
        date_views = new_date_views;
        var id = root.attr('data-date-id');
        if(id !== '') {
            date_ids_to_delete.push(id);
        }
        root.slideUp(function() {
            root.remove();
        });
    });

    // If there are no existing dates, simulate an "add date" button click, since they'll always
    // want to add a date in this case.
    if(existing_dates.length === 0) {
        add_date_button.click();
    }

    // Collect all dates on submit
    form.submit(function(e) {
        var date_objects = [];
        for(var i=0; i<date_views.length; i++) {
            date_objects.push(date_views[i].collectData());
        }
        dates_input.val(JSON.stringify(date_objects));
        dates_to_delete_input.val(JSON.stringify(date_ids_to_delete));
    });

});
