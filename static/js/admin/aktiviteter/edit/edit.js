$(function() {
    var scope = $('[data-dnt-container="aktivitet"]');

    scope.find('select[name="forening"]').select2();
    scope.find('select[name="co_forening"]').select2({ allowClear: true });
    scope.find('select[name="audiences"]').select2({ allowClear: true });
    scope.find('select[name="category_type"]').select2();
    scope.find('select[name="category_tags"]').select2({ allowClear: true });

    scope.find('button[data-dnt-action="remove-co-forening"]').on('click', function() {
        scope.find('select[name="co_forening"]').select2('val', null);
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
        $('select[name="category_type"]').select2("data", null);
        $('select[name="category_tags"]').select2("data", null);
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

    /**
     * DEMO: Code below is work in progress.
     * Simple toggling of fields, for demo purposes only
     */

    // DEMO: Images

    $("button.pick-from-image-archive").click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            $('.activity-picture-wrapper').removeClass('jq-hide');
            // TODO: Add to images container
        });
    });

    $("button.upload-new-image").click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            $('.activity-picture-wrapper').removeClass('jq-hide');
            // TODO: Add to images container
        });
    });
});

