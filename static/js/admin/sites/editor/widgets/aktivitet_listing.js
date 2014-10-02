$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function(editor) {
            editor.find('select[name="foreninger"]').select2();
            editor.find('select[name="audiences"]').select2();
        },

        onNew: function(editor) {
            // Default the organizer to the active forening of the current site
            var default_forening = editor.attr('data-dnt-active-forening');
            editor.find('select[name="foreninger"]').select2('val', default_forening);

            // Create an array with all available audiences and default to that
            var audiences = editor.find('select[name="audiences"]');
            var options = [];
            audiences.find('option').each(function() {
                options.push($(this).val());
            });
            audiences.select2('val', options);
        },

        onEdit: function(editor, widget_content) {
            editor.find('select[name="foreninger"]').select2('val', widget_content.foreninger);
            editor.find('select[name="audiences"]').select2('val', widget_content.audiences);
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'aktivitet_listing',
                foreninger: editor.find('select[name="foreninger"]').select2('val'),
                audiences: editor.find('select[name="audiences"]').select2('val'),
            });
            return true;
        }
    });
});
