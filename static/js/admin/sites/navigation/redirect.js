$(function() {

    var $editor = $('[data-dnt-container="menu-editor"]');

    var $redirect_add = $editor.find('[data-dnt-trigger="add-redirect"]');

    var $modal = $editor.find('[data-dnt-container="redirect-modal"]');
    var $modal_save_button = $modal.find('[data-dnt-trigger="save"]');
    var $modal_cancel_button = $modal.find('[data-dnt-trigger="cancel"]');
    var $modal_delete_button = $modal.find('[data-dnt-trigger="delete"]');

    var $form = $modal.find('form');
    var $form_existing_redirect = $form.find('input[name="existing-redirect"]');
    var $form_delete = $form.find('input[name="delete"]');
    var $form_path = $form.find('input[name="path"]');
    var $form_destination = $form.find('input[name="destination"]');

    // Add redirect
    $redirect_add.click(function() {
        // Reset input control state
        $form_existing_redirect.val('');
        $form_path.val('');
        $form_destination.val('');

        // Show only relevant buttons
        $modal_cancel_button.show();
        $modal_delete_button.hide();

        $modal.modal();
    });

    // Edit redirect
    $(document).on('click', $editor.selector + ' [data-dnt-trigger="edit-redirect"]', function() {
        // Reset input control states
        var $row = $(this).parents('[data-dnt-redirect]');
        $form_existing_redirect.val($row.attr('data-dnt-redirect'));
        $form_path.val($row.attr('data-dnt-path'));
        $form_destination.val($row.attr('data-dnt-destination'));

        // Show only relevant buttons
        $modal_cancel_button.hide();
        $modal_delete_button.show();

        $modal.modal();
    });

    /**
     * Modal logic
     */

    $modal_save_button.click(function() {
        $modal_save_button.prop('disabled', true);
        $modal_cancel_button.prop('disabled', true);
        $modal_delete_button.prop('disabled', true);
        $form.submit();
    });

    // Delete current item
    $modal_delete_button.click(function() {
        if(!confirm($modal_delete_button.attr('data-dnt-confirm-delete'))) {
            return;
        }

        $modal_save_button.prop('disabled', true);
        $modal_cancel_button.prop('disabled', true);
        $modal_delete_button.prop('disabled', true);

        $form_delete.val('1');
        $form.submit();
    });

});
