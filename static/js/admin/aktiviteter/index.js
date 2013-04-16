$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var actual_listing = listing.find("div.list-wrapper");
    var new_categories = listing.find("div.new-categories");
    var initial_category = new_categories.find("div.initial-category");
    var category_buttons = new_categories.find("button.category");
    var subcategories = new_categories.find("div.pick-subcategories");
    var subcategories_chosen = subcategories.find("div.chosen-category");
    var subcategories_other = subcategories.find("div.other-categories");
    var subcategories_hidden = subcategories.find("div.subcategories-hidden");
    var subcategories_buttons = subcategories.find("button.subcategory");
    var show_other_subcategories = subcategories.find("a.show-other-subcategories");

    var form = new_categories.find("form.create-new-category");
    var form_category = form.find("input[name='category']");
    var form_tags = form.find("input[name='tags']");
    var form_tag_box = form.find("div.tag-box");

    category_buttons.click(function() {
        form_category.val($(this).attr('data-tag-name'));
        var chosen_category = subcategories.find("div.subcategories." + $(this).attr('data-tag-name'));
        chosen_category.find("h3.chosen").show();
        chosen_category.detach().prependTo(subcategories_chosen);
        subcategories.slideDown();
        initial_category.remove();
        actual_listing.remove();
    });

    show_other_subcategories.click(function() {
        $(this).parent().remove();
        var other_subcategories = subcategories_hidden.children();
        other_subcategories.find("h3.other").show();
        other_subcategories.detach();
        other_subcategories.slice(0, 1).appendTo(subcategories_other.find("div.span4").slice(0, 1));
        other_subcategories.slice(1, 2).appendTo(subcategories_other.find("div.span4").slice(1, 2));
        other_subcategories.slice(2, 3).appendTo(subcategories_other.find("div.span4").slice(2, 3));
        subcategories_other.slideDown();
    });

    TaggerAH.enable({
        targetInput: form_tags
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
        if(TaggerAH.count() === 0) {
            alert("Du må legge til minst én kategori - velg fra knappene over.");
            e.preventDefault();
            return;
        }
        TaggerAH.collect();
    });

});
