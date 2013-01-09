(function(ArticleWidgetEditor, $, undefined ) {

    var widget_editor; // Gets set in the preparations below

    /* Document preparations */

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='articles']");

        // Enable/disable
        widget_editor.find("input[name='tag-link']").typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: '/tags/filter/',
                    data: 'name=' + encodeURIComponent(query)
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
        });
        widget_editor.find("input[name='set-tag-link']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tag-link']").removeAttr('disabled');
            } else {
                widget_editor.find("input[name='tag-link']").attr('disabled', true).val("");
            }
        });

        widget_editor.find("input[name='enable-tags']").change(function() {
            if($(this).is(':checked')) {
                widget_editor.find("input[name='tags']").removeAttr('disabled');
            } else {
                widget_editor.find("input[name='tags']").attr('disabled', true).val("");
                widget_editor.find("div.tag-box").empty();
            }
        });

        // Create the tagger object, make it globally accessible
        window.article_widget_tagger = new TypicalTagger(widget_editor.find("input[name='tags']"), widget_editor.find("div.tag-box"));

    });

}(window.ArticleWidgetEditor = window.ArticleWidgetEditor || {}, jQuery ));
