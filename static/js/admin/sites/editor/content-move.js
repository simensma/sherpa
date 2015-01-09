(function(EditorMoveContent, $, undefined ) {

    var moved_content;
    var endCallback;
    var editor;
    var article;
    var insertion_templates;
    var is_moving = false;
    var move_type_selector;
    var move_type_add_selector;

    $(function() {
        editor = $("div.cms-editor");
        article = editor.find("article");
        insertion_templates = editor.find('[data-dnt-container="insertion-templates"]');
    });

    EditorMoveContent.init = function(opts) {
        moved_content = opts.content;
        endCallback = opts.endCallback;

        if (moved_content.hasClass('content')) {
            move_type_selector = 'div.content';
            move_type_add_selector = 'div.add-content';

        } else if (moved_content.hasClass('row')) {
            move_type_selector = 'div.row[data-dnt-row]';
            move_type_add_selector = 'div.row.add-row';

        } else {
            return;
        }

        is_moving = true;

        // Hovered content will have the custom 'hover' class but the mouseover which is supposed to remove
        // it might not be triggered when moving is initiated, so explicitly remove it here
        moved_content.removeClass('hover');

        // Hide add-content fields and insert drop-areas below
        article.find(move_type_add_selector).each(function() {
            // Hide drop-areas adjacent to the content being moved
            if($(this).prevAll(move_type_selector).first().is(moved_content) || $(this).nextAll(move_type_selector).first().is(moved_content)) {
                // Just set visibility hidden so nothing jumps, and the controls will re-appear when reset
                $(this).css('visibility', 'hidden');
            } else {
                // Note that add-content and drop-area should always be the same height
                $(this).hide();
                insertion_templates.find('div.drop-area').clone().insertAfter($(this));
            }
        });

        // Disable most of the hover effects
        article.find("div.edit-structure button").tooltip('destroy');
        article.find(move_type_selector).addClass('moving');

        // Add hover effect to add-content elements
        article.find(move_type_add_selector + ':not(.disabled)').on('mouseover.EditorMoveContent', function() {
            $(this).addClass('droparea');
        });

        // An insertable drop-area was clicked, move the content there
        article.find("div.drop-area").click(function() {
            moved_content.detach().insertAfter($(this));

            // If the item was moved into a row with a sole add-content control and no content, it'll be missing the
            // data-dnt-row attribute, so add that
            var row = $(this).parents('.row');
            if(row.attr('data-dnt-row') === undefined) {
                row.attr('data-dnt-row', true);
            }
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

        // Remove the drop-area controls
        article.find('div.drop-area').remove();

        // And call our given endCallback. It's the callback's responsibility to clean up
        // moving states on controls etc.
        endCallback();
    };

    EditorMoveContent.isMoving = function() {
        return is_moving;
    };

}(window.EditorMoveContent = window.EditorMoveContent || {}, jQuery ));
