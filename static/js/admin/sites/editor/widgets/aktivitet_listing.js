$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function($editor) {
            $editor.find('select[name="foreninger"]').select2();
            $editor.find('select[name="audiences"]').select2();
            $editor.find('select[name="categories"]').select2();

            $editor.find('[data-dnt-trigger="edit-filters"]').click(function() {
                $editor.find('[data-dnt-container="edit-filters"]').hide();
                $editor.find('[data-dnt-container="filters"]').slideDown();
            });

            var $limit = $editor.find('input[name="limit"]');
            var $save = $editor.find('button.save');

            $limit.on('input', function () {
                var val = parseInt($(this).val(), 10);
                if (val > 50) {
                    $(this).parents('[data-dnt-container]').first().addClass('has-error');
                    $(this).focus();
                    $save.attr('disabled', true);

                } else {
                    $(this).parents('[data-dnt-container]').first().removeClass('has-error');
                    $save.attr('disabled', false);
                }
            });
        },

        onNew: function($editor) {
            // Default the organizer to the active forening of the current site
            var default_forening = $editor.attr('data-dnt-active-forening');
            $editor.find('select[name="foreninger"]').select2('val', default_forening);

            // Hide editable filter controls by default
            $editor.find('[data-dnt-container="edit-filters"]').show();
            $editor.find('[data-dnt-container="filters"]').hide();

            // Default to all available audiences and categories
            var audiences = $editor.find('select[name="audiences"]');
            var categories = $editor.find('select[name="categories"]');
            audiences.select2('val', allOptionsFor(audiences));
            categories.select2('val', allOptionsFor(categories));
        },

        onEdit: function($editor, widget_content) {
            $editor.find('select[name="foreninger"]').select2('val', widget_content.foreninger);
            $editor.find('select[name="audiences"]').select2('val', widget_content.audiences);
            $editor.find('select[name="categories"]').select2('val', widget_content.categories);

            var audience_options = allOptionsFor($editor.find('select[name="audiences"]'));
            var category_options = allOptionsFor($editor.find('select[name="categories"]'));

            if(widget_content.audiences.length == audience_options.length &&
                widget_content.categories.length == category_options.length) {
                // This widget is configured to show all audiences and categories; hide filter controls
                $editor.find('[data-dnt-container="edit-filters"]').show();
                $editor.find('[data-dnt-container="filters"]').hide();
            } else {
                // User has changed audiences and/or categories; show the controls
                $editor.find('[data-dnt-container="edit-filters"]').hide();
                $editor.find('[data-dnt-container="filters"]').show();
            }

        },

        onSave: function($editor) {
            var $audiences = $editor.find('select[name="audiences"]');
            var $categories = $editor.find('select[name="categories"]');
            var $limit = $editor.find('input[name="limit"]');

            var audiences = $audiences.select2('val');
            var categories = $categories.select2('val');
            var limit = $limit.val() || 50;

            if(audiences.length === 0) {
                audiences = allOptionsFor($audiences);
            }

            if(categories.length === 0) {
                categories = allOptionsFor($categories);
            }

            WidgetEditor.saveWidget({
                widget: 'aktivitet_listing',
                foreninger: $editor.find('select[name="foreninger"]').select2('val'),
                audiences: audiences,
                categories: categories,
                limit: limit
            });
            return true;
        }
    });

    function allOptionsFor(select) {
        // Create an array with all available options in the given select
        var options = [];
        select.find('option').each(function() {
            options.push($(this).val());
        });
        return options;
    }
});
