$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function(editor) {
            editor.find('select[name="foreninger"]').select2();
            editor.find('select[name="audiences"]').select2();
            editor.find('select[name="categories"]').select2();
        },

        onNew: function(editor) {
            // Default the organizer to the active forening of the current site
            var default_forening = editor.attr('data-dnt-active-forening');
            editor.find('select[name="foreninger"]').select2('val', default_forening);

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
