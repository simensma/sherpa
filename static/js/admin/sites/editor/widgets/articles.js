$(function() {

    var $tags_enabled;
    var $tags_input;

    WidgetEditor.listen({
        widget_name: 'articles',

        init: function($editor) {
            $tags_enabled = $editor.find('input[name="enable-tags"]');
            $tags_input = $editor.find('input[name="tags"]');

            $editor.find("input[name='layout']").click(function() {
                if($editor.find("input[name='layout']:checked").val() === 'medialist') {
                    $editor.find("div.medialist-section").show();
                    $editor.find("div.horizontal-section").hide();
                } else {
                    $editor.find("div.medialist-section").hide();
                    $editor.find("div.horizontal-section").show();
                }
            });

            // Enable/disable
            var url = $editor.find("input[name='tag-link']").attr('data-tags-url');
            $editor.find("input[name='tag-link']").typeahead({
                minLength: 3,
                remote: url + "?q=%QUERY"
            });
            $editor.find("input[name='set-tag-link']").change(function() {
                if($(this).is(':checked')) {
                    $editor.find("input[name='tag-link']").prop('disabled', false);
                } else {
                    $editor.find("input[name='tag-link']").prop('disabled', true).val("");
                }
            });

            $tags_enabled.change(function() {
                var enabled = $(this).is(':checked');
                $tags_input.select2('enable', enabled);
                if(!enabled) {
                    $tags_input.select2('val', '');
                }
            });

            Select2Tagger({$input: $tags_input});
        },

        onNew: function($editor) {
            $tags_enabled.prop('checked', false);
            $tags_input.select2('val', '').select2('enable', false);
        },

        onEdit: function($editor, widget_content) {
            $editor.find("input[name='layout'][value='" + widget_content.layout + "']").click();
            if(widget_content.layout === 'medialist') {
                $editor.find("div.medialist-section").show();
                $editor.find("div.horizontal-section").hide();
            } else {
                $editor.find("div.medialist-section").hide();
                $editor.find("div.horizontal-section").show();
            }
            $editor.find("select[name='columns'] option[value='" + widget_content.columns + "']").prop('selected', true);
            $editor.find("input[name='title']").val(widget_content.title);
            $editor.find("input[name='count']").val(widget_content.count);
            $editor.find("input[name='display-images']").prop('checked', widget_content.display_images);
            if(widget_content.tag_link === null) {
                $editor.find("input[name='set-tag-link']").prop('checked', false);
                $editor.find("input[name='tag-link']").prop('disabled', true).val("");
            }

            // Can't use empty array to clear select2, must use empty string
            $tags_input.select2('val', widget_content.tags.length > 0 ? widget_content.tags : '');

            var has_tags = widget_content.tags.length > 0;
            $tags_enabled.prop('checked', has_tags);
            $tags_input.select2('enable', has_tags);
        },

        onSave: function($editor) {
            var layout = $editor.find("input[name='layout']:checked").val();

            var title;
            var count;
            var columns;
            if(layout === 'medialist') {
                count = $editor.find("input[name='count']").val();
                if(isNaN(Number(count))) {
                    alert("Du må angi et tall for antall nyheter som skal vises!");
                    return false;
                } else if(count < 1) {
                    alert("Du må vise minst én nyhet!");
                    return false;
                }
                title = $editor.find("input[name='title']").val();

                // Set unused default value for columns
                columns = 2;
            } else if(layout === 'horizontal') {
                columns = $editor.find("select[name='columns'] option:selected").val();

                // Set unused default value for count/title
                count = 1;
                title = '';
            } else {
                alert("Du må velge om visningen skal være stående eller liggende.");
                return false;
            }

            var display_images = $editor.find("input[name='display-images']").prop('checked');
            var tag_link;
            if($editor.find("input[name='set-tag-link']").is(':checked')) {
                tag_link = $editor.find("input[name='tag-link']").val();
            } else {
                tag_link = null;
            }
            var tags;
            if($tags_enabled.is(':checked')) {
                tags = $tags_input.select2('val');
            } else {
                tags = [];
            }

            WidgetEditor.saveWidget({
                widget: "articles",
                layout: layout,
                title: title,
                count: count,
                columns: columns,
                display_images: display_images,
                tag_link: tag_link,
                tags: tags,
            });
            return true;
        }
    });
});
