$(function() {

    WidgetEditor.listen({
        widget_name: 'blog',

        onEdit: function(editor, widget_content) {
            editor.find("input[name='count']").val(widget_content.count);
            editor.find("select[name='category']").val(widget_content.category);
        },

        onSave: function(editor) {
            var count = editor.find("input[name='count']").val();
            var category = editor.find("select[name='category']").val();

            if(isNaN(Number(count))) {
                alert("Du må angi et tall for antall blogginnlegg som skal vises!");
                return false;
            } else if(count < 1) {
                alert("Du må vise minst ett blogginnlegg!");
                return false;
            }

            WidgetEditor.saveWidget({
                widget: "blog",
                count: count,
                category : category
            });
            return true;
        }
    });

});
