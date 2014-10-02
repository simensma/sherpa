$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function(editor) {
            editor.find('select[name="foreninger"]').select2();
            editor.find('select[name="audiences"]').select2();
            editor.find('select[name="categories"]').select2();

            editor.find('[data-dnt-trigger="edit-filters"]').click(function() {
                editor.find('[data-dnt-container="edit-filters"]').hide();
                editor.find('[data-dnt-container="filters"]').slideDown();
            });
        },

        onNew: function(editor) {
            // Default the organizer to the active forening of the current site
            var default_forening = editor.attr('data-dnt-active-forening');
            editor.find('select[name="foreninger"]').select2('val', default_forening);

            // Hide editable filter controls by default
            editor.find('[data-dnt-container="edit-filters"]').show();
            editor.find('[data-dnt-container="filters"]').hide();

            // Create an array with all available audiences and default to that
            var audiences = editor.find('select[name="audiences"]');
            var audience_options = [];
            audiences.find('option').each(function() {
                audience_options.push($(this).val());
            });
            audiences.select2('val', audience_options);

            // Create an array with all available categories and default to that
            var categories = editor.find('select[name="categories"]');
            var category_options = [];
            categories.find('option').each(function() {
                category_options.push($(this).val());
            });
            categories.select2('val', category_options);
        },

        onEdit: function(editor, widget_content) {
            editor.find('select[name="foreninger"]').select2('val', widget_content.foreninger);
            editor.find('select[name="audiences"]').select2('val', widget_content.audiences);
            editor.find('select[name="categories"]').select2('val', widget_content.categories);

            // Create an array with all available audiences and default to that
            var audiences = editor.find('select[name="audiences"]');
            var audience_options = [];
            audiences.find('option').each(function() {
                audience_options.push($(this).val());
            });

            // Create an array with all available categories and default to that
            var categories = editor.find('select[name="categories"]');
            var category_options = [];
            categories.find('option').each(function() {
                category_options.push($(this).val());
            });

            if(widget_content.audiences.length == audience_options.length &&
                widget_content.categories.length == category_options.length) {
                // This widget is configured to show all audiences and categories; hide filter controls
                editor.find('[data-dnt-container="edit-filters"]').show();
                editor.find('[data-dnt-container="filters"]').hide();
            } else {
                // User has changed audiences and/or categories; show the controls
                editor.find('[data-dnt-container="edit-filters"]').hide();
                editor.find('[data-dnt-container="filters"]').show();
            }

        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'aktivitet_listing',
                foreninger: editor.find('select[name="foreninger"]').select2('val'),
                audiences: editor.find('select[name="audiences"]').select2('val'),
                categories: editor.find('select[name="categories"]').select2('val'),
            });
            return true;
        }
    });
});
