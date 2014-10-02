$(function() {

    WidgetEditor.listen({
        widget_name: 'aktivitet_listing',

        init: function(editor) {
            editor.find('select[name="foreninger"]').select2();
        },

        onNew: function(editor) {
            var default_forening = editor.attr('data-dnt-active-forening');
            editor.find('select[name="foreninger"]').select2('val', default_forening);
        },

        onEdit: function(editor, widget_content) {
            editor.find('select[name="foreninger"]').select2('val', widget_content.foreninger);
        },

        onSave: function(editor) {
            WidgetEditor.saveWidget({
                widget: 'aktivitet_listing',
                foreninger: editor.find('select[name="foreninger"]').select2('val'),
            });
            return true;
        }
    });
});
