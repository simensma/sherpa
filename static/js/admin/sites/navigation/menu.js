$(function() {

    // Set when a modal is opened (undefined for new items, or the anchor element for editing)
    var activeMenu;

    var menus = $("nav#menus");
    var menu_modal = $("div.modal.menu");
    var menu_add = $("a.add-menu-element");
    var loading = menu_modal.find("div.loading");
    var save_button = menu_modal.find("button.save-menu");
    var delete_button = menu_modal.find("button.delete-menu");

    var address = menu_modal.find('[data-dnt-text="address"]');
    var edit_address = menu_modal.find('[data-trigger="edit-address"]');

    menu_add.click(function() {
        activeMenu = undefined;
        menu_modal.find("input[name='name']").val('');
        address.text('');
        delete_button.hide();
        menu_modal.modal();
    });

    menus.find("a.edit").click(edit);

    function edit() {
        activeMenu = $(this);
        menu_modal.find("input[name='name']").val($(this).text());
        address.text($(this).attr('data-href'));
        delete_button.show();
        menu_modal.modal();
    }

    edit_address.click(function() {
        UrlPicker.open({
            disable_email: true,
            existing_url: address.text().trim(),
            done: function(result) {
                address.text(result.url);
            },
        });
    });

    menus.find("ul").sortable({
        vertical: false,
        nested: false,
        onDrop: function ($item, container, _super) {
            _super($item, container);
            var list = $(this);
            var i = 0;
            var items = [];
            menus.find("a.edit").each(function() {
                items.push({
                    "id": $(this).attr('data-id'),
                    "order": i
                });
                i++;
            });
            $.ajaxQueue({
                url: menus.attr('data-reorder-url'),
                data: { menus: JSON.stringify(items) }
            }).fail(function(result) {
                alert("Klarte ikke å lagre ny menyposisjon, vennligst oppdater siden (F5) og prøv igjen.");
            });
        }
    });

    save_button.click(function() {
        var name = menu_modal.find("input[name='name']").val().trim();
        var url = address.text();
        if(!url.match(/^https?:\/\//) && !url.startsWith('/')) {
            url = "http://" + url;
        }
        if(name === '' || url === '') {
            alert("Skriv inn både navn og adresse for lenken.");
            return;
        }
        var ajaxUrl;
        var id;
        if(activeMenu === undefined) {
            ajaxUrl = menu_modal.attr('data-new-url');
        } else {
            ajaxUrl = menu_modal.attr('data-edit-url');
            id = activeMenu.attr('data-id');
        }
        loading.show();
        save_button.prop('disabled', true);
        delete_button.prop('disabled', true);
        $.ajaxQueue({
            url: ajaxUrl,
            data: {
                name: name,
                url: url,
                id: id
            }
        }).done(function(result) {
            if(activeMenu === undefined) {
                result = JSON.parse(result);
                var item = $('<li><a class="edit" data-id="' + result.id + '" data-href="' + url + '"  href="javascript:undefined">' + name + '</a></li>');
                item.find("a.edit").click(edit);
                if(menus.find("li").length > 0) {
                    menus.find("li").last().after(item);
                } else {
                    menus.find("ul").append(item);
                }
            } else {
                activeMenu.text(name);
                activeMenu.attr('data-href', url);
            }
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil ved lagring av menyen. Vennligst prøv igjen.");
        }).always(function(result) {
            save_button.prop('disabled', false);
            delete_button.prop('disabled', false);
            loading.hide();
            menu_modal.modal('hide');
        });
    });

    delete_button.click(function() {
        if(!confirm('Er du sikker på at du vil slette denne linken fra hovedmenyen?')) {
            return;
        }
        var url = menu_modal.attr('data-delete-url');
        loading.show();
        save_button.prop('disabled', true);
        delete_button.prop('disabled', true);
        $.ajaxQueue({
            url: url,
            data: { menu: activeMenu.attr('data-id') }
        }).done(function(result) {
            activeMenu.parents("li").remove();
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil ved sletting av elementet. Vennligst prøv igjen.");
        }).always(function(result) {
            save_button.prop('disabled', false);
            delete_button.prop('disabled', false);
            loading.hide();
            menu_modal.modal('hide');
        });
    });
});
