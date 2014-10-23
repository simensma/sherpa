$(function() {
    var scope = $('[data-dnt-container="aktivitet"]');

    scope.find('select[name="forening"]').select2();
    scope.find('select[name="co_foreninger[]"]').select2({ allowClear: true });
    scope.find('select[name="audiences"]').select2({ allowClear: true });
    scope.find('select[name="category_type"]').select2();
    scope.find('select[name="category_tags"]').select2({ allowClear: true });
    scope.find('[data-dnt-container="pub-date"]').datepicker({
        format: 'dd.mm.yyyy',
        language: 'no',
        autoclose: true,
        weekStart: 1
    });

    scope.find('button[data-dnt-action="remove-co-foreninger"]').on('click', function() {
        // Single selects should be set to empty string ""
        scope.find('select[name="co_foreninger[]"]').select2('val', '');
    });

    scope.find('button[data-dnt-action="remove-category-tags"]').on('click', function() {
        // Multi selects should be set to empty array []
        scope.find('select[name="category_tags"]').select2('val', []);
    });

    scope.find('input[name="category"]').on('change', function() {
        var cat = $(this).val();

        // This changes the label for subcategory based on category
        scope.find('[data-dnt-container="subcategory-label"]').attr('class', 'selected ' + cat);

        // Move subcategory options to tag select
        $('select[name="category_type"] option').each(function() {
            if ($(this).val() === '') { return; }

            $(this).removeAttr('selected');
            $(this).detach().appendTo('select[name="category_tags"]');
        });

        // Move correct tags to subcategory select
        $('select[name="category_tags"] option.' + cat).each(function() {
            $(this).removeAttr('selected');
            $(this).detach().appendTo('select[name="category_type"]');
        });

        // Reset subcategory and tag select
        $('select[name="category_type"]').select2('val', '');
        $('select[name="category_tags"]').select2('val', []);
    });

    // Show/hide publish details
    scope.find('input[name="publish"]').change(function() {
        var hide = !$(this).is(':checked');
        scope.find('[data-dnt-container="published-extras"]').toggleClass('jq-hide', hide);
    });

    // Prevent non-submit buttons from submitting
    scope.find('button:not([type="submit"])').on('click', function(e) {
        e.preventDefault();
    });

    // Prevent pressing the submit button twice
    scope.submit(function(e) {
        scope.find('button[type="submit"]').prop('disabled', true);
    });
});


$(function() {
    var scope = $('[data-dnt-container="import"]');

    // On submit, disable submit button and display loading gif
    scope.submit(function() {
        scope.find('button[type="submit"]').prop('disabled', true);
        scope.find('[data-dnt-container="help-block"]').hide();
        scope.find('[data-dnt-container="loading"]').show();
    });
});
