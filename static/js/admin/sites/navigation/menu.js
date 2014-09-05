$(function() {

    var $editor = $('[data-dnt-container="menu-editor"]');

    var $menus = $editor.find('[data-dnt-container="main-menu"]');
    var $menu_list = $menus.find('[data-dnt-container="menu-list"]');
    var $menu_add = $editor.find('[data-dnt-trigger="add-menu-item"]');
    var $success = $editor.find('[data-dnt-container="success"]');
    var $loading = $editor.find('[data-dnt-container="loading"]');
    var $menu_item_template = $editor.find('[data-dnt-container="menu-item-template"]');

    var $modal = $editor.find('[data-dnt-container="menu-modal"]');
    var $modal_name = $modal.find('input[name="name"]');
    var $modal_save_button = $modal.find('[data-dnt-trigger="save"]');
    var $modal_cancel_button = $modal.find('[data-dnt-trigger="cancel"]');
    var $modal_delete_button = $modal.find('[data-dnt-trigger="delete"]');
    var $modal_address = $modal.find('[data-dnt-text="address"]');
    var $modal_edit_address = $modal.find('[data-trigger="edit-address"]');

    // Reference to the menu list item being edited in modal, or an empty jquery object if new item
    var $edited_menu;

    // Add menu item
    $menu_add.click(function() {
        // New menu
        $edited_menu = $();

        // Reset input control state
        $modal_name.val('');
        $modal_address.text('');

        // Show only relevant buttons
        $modal_cancel_button.show();
        $modal_delete_button.hide();

        $modal.modal();
    });

    // Edit menu item
    $(document).on('click', $menus.selector + ' [data-dnt-menu-item]', function() {
        // Editing menu item
        $edited_menu = $(this).parent();

        // Reset input control states
        $modal_name.val($(this).text());
        $modal_address.text($(this).attr('data-dnt-href'));

        // Show only relevant buttons
        $modal_cancel_button.hide();
        $modal_delete_button.show();

        $modal.modal();
    });

    // Sort menu items
    $menus.find('ul').sortable({
        vertical: false,
        nested: false,
        onDrop: function ($item, container, _super) {
            _super($item, container);
            save();
        }
    });

    // Save current menu state
    function save() {
        $success.hide();
        $loading.show();

        var menu_list = [];
        var abort = false;
        $menus.find('[data-dnt-menu-item]').each(function() {
            menu_list.push({
                name: $(this).text().trim(),
                url: $(this).attr('data-dnt-href').trim(),
            });
        });

        $.ajaxQueue({
            url: $menus.attr('data-dnt-save-url'),
            data: { menus: JSON.stringify(menu_list) },
        }).done(function(result) {
            $success.show();
        }).fail(function(result) {
            alert($menus.attr('data-dnt-save-failure'));
        }).always(function(result) {
            $loading.hide();
        });
        return true;
    }

    /**
     * Modal logic
     */

    // Save current item
    $modal_save_button.click(function() {
        var name = $modal_name.val().trim();
        var url = $modal_address.text().trim();

        if(name === '') {
            alert($menus.attr('data-dnt-empty-name'));
            return;
        }

        if(url === '') {
            alert($menus.attr('data-dnt-empty-url'));
            return;
        }

        var $menu_item;

        if($edited_menu.length === 0) {
            $menu_item = $menu_item_template.clone();
            $menu_item.removeAttr('data-dnt-container');
            $menu_item.appendTo($menu_list);
        } else {
            $menu_item = $edited_menu;
        }

        var anchor = $menu_item.find('[data-dnt-menu-item]');
        anchor.text(name);
        anchor.attr('data-dnt-href', url);

        if(save()) {
            $modal.modal('hide');
        }
    });

    // Delete current item
    $modal_delete_button.click(function() {
        if(!confirm($menus.attr('data-dnt-confirm-delete-item'))) {
            return;
        }

        $edited_menu.remove();
        if(save()) {
            $modal.modal('hide');
        }
    });

    // Edit URl address
    $modal_edit_address.click(function() {
        UrlPicker.open({
            disable_email: true,
            existing_url: $modal_address.text().trim(),
            done: function(result) {
                $modal_address.text(result.url);
            },
        });
    });

});
