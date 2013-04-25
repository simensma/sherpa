$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var actual_listing = listing.find("div.list-wrapper");
    var new_categories = listing.find("div.new-categories");
    var initial_category = new_categories.find("div.initial-category");
    var category_buttons = new_categories.find("button.category");
    var subcategories = new_categories.find("div.pick-subcategories");
    var subcategories_picked = subcategories.find("div.picked");
    var subcategories_buttons = subcategories.find("button.subcategory");
    var more_categories = new_categories.find("div.more-categories");

    var tag_input = subcategories.find("div.subcategories.custom input[name='tagger']");
    var tag_box = subcategories.find("div.subcategories.custom div.tag-box");

    var form = new_categories.find("form.create-new-category");
    var form_category = form.find("input[name='category']");
    var form_tags = form.find("input[name='tags']");

    category_buttons.click(function() {
        initial_category.hide();
        actual_listing.hide();
        var category_name = $(this).attr('data-tag-name');
        form_category.val(category_name);
        more_categories.find("p.choices a[data-category='" + category_name + "']").parent().remove();
        var category = subcategories.find("div.subcategories." + category_name);
        category.find("h3.chosen").show();
        category.detach().appendTo(subcategories_picked).show();
        subcategories.slideDown();
    });

    more_categories.find("p.choices a").click(function() {
        $(this).replaceWith($(this).text());
        var category_name = $(this).attr('data-category');
        var category = subcategories.find("div.subcategories." + category_name);
        if(category_name != 'custom') {
            category.find("h3.extra").show();
            category.detach().appendTo(subcategories_picked);
        }
        category.slideDown();

        // Remove the choices if all choices have been picker
        if(more_categories.find("p.choices a").length === 0) {
            more_categories.hide();
        }
    });

    TagDisplayAH.enable({
        targetInput: form_tags,
        pickerInput: tag_input,
        tagBox: tag_box
    });

    subcategories_buttons.click(function() {
        if($(this).is(".btn-danger")) {
            TaggerAH.removeTag($(this).text());
            $(this).removeClass("btn-danger");
        } else {
            var result = TaggerAH.addTag($(this).text());
            if(result.status === 'ok') {
                $(this).addClass("btn-danger");
            }
        }
    });

    form.submit(function(e) {
        if(TagDisplayAH.count() === 0) {
            alert("Du må legge til minst én kategori - velg fra knappene over.");
            e.preventDefault();
            return;
        }
        TagDisplayAH.collect();
    });

});
