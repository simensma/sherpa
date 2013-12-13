$(document).ready(function() {

    var editor = $("div.admin-aktivitet-edit");
    var form = editor.find("form.edit-aktivitet");
    var private_aktivitet = form.find("div.control-group.private_aktivitet");
    var category = form.find("div.control-group.category");
    var category_input = category.find("input[name='category']");
    var category_buttons = category.find("button[data-category]");
    var subcategories = form.find("div.control-group.subcategories");
    var subcategory_labels = subcategories.find("div.labels");
    var subcategory_main_buttons = subcategories.find("div.main-buttons");
    var subcategory_other_buttons = subcategories.find("div.other-buttons");
    var subcategory_other_buttons_wrapper = subcategories.find("div.other-buttons-wrapper");
    var subcategory_other_buttons_trigger = subcategories.find("a.show-other-buttons");
    var custom_subcategory = subcategories.find("input[name='custom-category']");
    var subcategory_input = subcategories.find("input[name='subcategories']");
    var association_select = form.find("select[name='association']");
    var co_association_select = form.find("select[name='co_association']");
    var images_input = form.find("input[name='images']");

    var images = form.find("div.control-group.images");
    var images_initiate = images.find("div.images-initiate");
    var images_container = images.find("div.images");

    images_initiate.find("a").click(function() {
        images_initiate.hide();
        images_container.slideDown();
    });

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

    category_buttons.click(function() {
        subcategory_labels.find("h3").hide();
        subcategory_labels.find("h3." + $(this).attr('data-category')).show();

        // Move all main buttons back

        subcategory_main_buttons.find("button.subcategory").each(function() {
            $(this).detach();
            subcategory_other_buttons.append(' ');
            subcategory_other_buttons.append($(this));
        });

        subcategory_other_buttons.find("button.subcategory." + $(this).attr('data-category')).each(function() {
            $(this).detach();
            subcategory_main_buttons.append(' ');
            subcategory_main_buttons.append($(this));
        });
    });

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

    subcategory_main_buttons.find("button.subcategory").click(toggleButtons);
    subcategory_other_buttons.find("button.subcategory").click(toggleButtons);

    subcategory_other_buttons_trigger.click(function() {
        $(this).parent().hide();
        subcategory_other_buttons_wrapper.slideDown();
    });

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
        },
        updater: function(item) {
            custom_subcategory.val(item);
            addCustomSubcategory();
        }
    });

    custom_subcategory.keyup(function(e) {
        if(e.which == 13) { // Enter
            addCustomSubcategory();
            e.preventDefault();
        }
    });

    function addCustomSubcategory() {
        var categories = custom_subcategory.val().trim().split(' ');
        for(var i=0; i<categories.length; i++) {
            if(categories[i] === '') {
                continue;
            }

            // Check if the tag already exists
            main_existing = subcategory_main_buttons.find("button.subcategory:contains('" + categories[i] + "')");
            other_existing = subcategory_other_buttons.find("button.subcategory:contains('" + categories[i] + "')");
            if(main_existing.length > 0 || other_existing.length > 0) {
                main_existing.addClass("btn-danger");
                other_existing.addClass("btn-danger");
                custom_subcategory.val('');
                continue;
            }

            // Create the new button
            var new_button = subcategories.find("button.subcategory.fake").clone();
            new_button.text(categories[i]);
            new_button.removeClass('fake');
            subcategory_other_buttons.append(' ');
            subcategory_other_buttons.append(new_button);
            new_button.click(toggleButtons);
            new_button.show();
            custom_subcategory.val('');

            // This might be hidden, instashow it in this case
            subcategory_other_buttons_trigger.hide();
            subcategory_other_buttons_wrapper.slideDown();
        }
    }

    // Buttons without submit-type aren't supposed to submit the form
    $(document).on('click', "button:not([type='submit'])", function(e) {
        e.preventDefault();
    });

    // Dates
    var dates = form.find("div.section.dates");
    var dates_input = dates.find("input[name='dates']");
    var dates_to_delete_input = dates.find("input[name='dates_to_delete']");
    var existing_dates = dates.find("div.date-root:not(.hide)");
    var add_date_button = dates.find("button.add-date");
    var delete_date_modal = editor.find("div.modal.delete-date");
    var delete_date_loading = delete_date_modal.find("div.loading");
    var delete_date_preview = delete_date_modal.find("div.date-preview");
    var delete_date_fail = delete_date_modal.find("div.fail");
    var delete_date_choose = delete_date_modal.find("div.choose");
    var delete_date_confirm = delete_date_choose.find("button.confirm");
    var delete_date_cancel = delete_date_choose.find("button.cancel");

    var date_radio_counter = 0;
    var date_ids_to_delete = [];

    existing_dates.each(function() {
        $(this).data('view', new AktiviteterDatesView({
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
        new_root.data('view', new AktiviteterDatesView({
            root: new_root
        }));
        new_root.insertBefore(hidden_root);
        new_root.slideDown();
    });

    $(document).on('click', dates.selector + ' a.delete-date', function() {
        delete_date_loading.show();
        delete_date_choose.hide();
        delete_date_preview.empty();
        delete_date_fail.hide();
        delete_date_modal.modal();
        var date = $(this).parents("div.date-root");
        delete_date_modal.data('date-root', date);
        $.ajaxQueue({
            url: date.attr('data-delete-preview-url'),
            data: { date: date.attr('data-date-id') }
        }).done(function(result) {
            result = JSON.parse(result);
            delete_date_preview.append(result.html);
            delete_date_choose.show();
        }).fail(function() {
            delete_date_fail.show();
        }).always(function() {
            delete_date_loading.hide();
        });
    });

    delete_date_confirm.click(function() {
        if(!confirm($(this).attr('data-confirm'))) {
            return $(this);
        }

        delete_date_modal.modal('hide');

        var root = delete_date_modal.data('date-root');
        var id = root.attr('data-date-id');
        if(id !== '') {
            date_ids_to_delete.push(id);
        }
        root.slideUp(function() {
            root.remove();
        });
    });

    delete_date_cancel.click(function() {
        delete_date_modal.modal('hide');
    });

    // If there are no existing dates, simulate an "add date" button click, since they'll always
    // want to add a date in this case.
    if(existing_dates.length === 0) {
        add_date_button.click();
    }

    // Save buttons are disabled by default and enabled at window load, because if someone
    // clicks it before the window is fully loaded, inputs that are filled by js on form
    // submit may be missed
    $(window).load(function() {
        form.find("button[type='submit']").prop('disabled', false);
    });


    /**
     * Common submit operations
     */
    form.submit(function(e) {
        // Disable submit buttons
        $(this).find("button[type='submit']").prop('disabled', true);
        $(this).find("img.ajaxloader.submit").show();

        var priv = private_aktivitet.find("button.active").is(".private");
        private_aktivitet.find("input[name='private']").val(JSON.stringify(priv));
        images_input.val(JSON.stringify(ImageCarouselPicker.getImages()));

        // Collect the active category
        category_input.val(category_buttons.filter(".active").attr('data-category'));

        // Collect subcategory tags
        var tags = [];
        subcategory_main_buttons.find("button.btn-danger").each(function() {
            tags.push($(this).text());
        });
        subcategory_other_buttons.find("button.btn-danger").each(function() {
            tags.push($(this).text());
        });
        subcategory_input.val(JSON.stringify(tags));

        // Collect all currently active dates
        var date_objects = [];
        dates.find("div.date-root:not(.hide)").each(function() {
            date_objects.push($(this).data('view').collectData());
        });
        dates_input.val(JSON.stringify(date_objects));
        dates_to_delete_input.val(JSON.stringify(date_ids_to_delete));

        // Validate the form
        var validation = AktivitetValidator.validate();
        if(!validation.valid) {
            $(this).find("button[type='submit']").prop('disabled', false);
            $(this).find("img.ajaxloader.submit").hide();
            e.preventDefault();
            $('html, body').animate({
                scrollTop: validation.scrollTo.offset().top
            }, 300);
        }
    });

});
