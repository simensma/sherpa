(function(EditorMoveContent, $, undefined ) {

    var moved_content;
    var endCallback;
    var editor;
    var article;
    var is_moving = false;

    $(function() {
        editor = $("div.cms-editor");
        article = editor.find("article");
    });

    EditorMoveContent.init = function(opts) {
        moved_content = opts.content;
        endCallback = opts.endCallback;

        is_moving = true;

        // Mark the current icon as active
        moved_content.find("div.move-content").addClass('moving');

        // Disable the drop areas adjacent to the content being moved
        moved_content.prevAll('div.add-content').first().addClass('disabled');
        moved_content.nextAll('div.add-content').first().addClass('disabled');

        // Disable most of the hover effects
        article.find("div.edit-structure button").tooltip('destroy');
        article.find("div.add-content,div.add-content-row").addClass('moving').tooltip('destroy');
        article.find("div.content").addClass('moving');

        // Add hover effect to add-content elements
        article.find("div.add-content:not(.disabled)").on('mouseover.EditorMoveContent', function() {
            $(this).addClass('droparea');
        });

        // An insertable add-content element was clicked, move the content there
        article.find("div.add-content:not(.disabled)").click(function() {
            moved_content.detach().insertAfter($(this));
        });

        // Any click ends the moving session
        $(document.body).on("click.EditorMoveContent", function(e) {
            e.preventDefault();
            e.stopPropagation();
            EditorMoveContent.end();
        });

    };

    EditorMoveContent.end = function() {
        is_moving = false;

        // Remove all global drag-event listeners
        $(document.body).off("mouseup.EditorMoveContent");
        $(document.body).off("mousemove.EditorMoveContent");
        $(document.body).off("click.EditorMoveContent");

        // Reset contents to their normal state
        article.find("div.content").removeClass('moving');

        // Explicitly remove the content-controls from the dragged content since its mouseover
        // was ignored during the moving session
        moved_content.find("div.content-control").remove();

        // And call our given endCallback
        endCallback();
    };

    EditorMoveContent.isMoving = function() {
        return is_moving;
    };

}(window.EditorMoveContent = window.EditorMoveContent || {}, jQuery ));
