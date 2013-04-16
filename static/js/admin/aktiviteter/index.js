$(document).ready(function() {
    var listing = $("div.aktivitet-listing");
    var new_categories = listing.find("div.new-categories");
    var form = new_categories.find("form.create-new-category");
    var form_category = form.find("input[name='category']");

    form.find("input[type='submit']").click(function() {
        form_category.val($(this).attr('data-tag-name'));
    });
});
