/* Editing a page (not its contents) */

$(document).ready(function() {

    $("table#page-details a.delete-page").click(function(e) {
        if(!confirm("Er du sikker på at du vil slette hele denne siden, alle dens versjoner og varianter, og alt dens innhold FOR GODT? Denne handlingen kan du ikke angre!")) {
            e.preventDefault();
        }
    });

});

/* Menus */

$(document).ready(function() {

    // Set when a dialog is opened (undefined for new items, or the anchor element for editing)
    var activeMenu;

    $("nav#menus a.new").click(function() {
        activeMenu = undefined;
        var dialog = $("div.menu-dialog");
        dialog.find("input[name='name']").val('');
        dialog.find("input[name='url']").val('');
        $("div.menu-dialog button.delete-menu").hide();
        dialog.dialog('open');
    });

    $("nav#menus a.edit").click(edit);

    function edit() {
        activeMenu = $(this);
        var dialog = $("div.menu-dialog");
        dialog.find("input[name='name']").val($(this).text());
        dialog.find("input[name='url']").val($(this).attr('data-href'));
        $("div.menu-dialog button.delete-menu").show();
        dialog.dialog('open');
    }

    $("nav#menus ul").sortable({
        items: 'li:not(.new)',
        update: function() {
            var list = $(this);
            list.sortable('disable');
            var i = 0;
            var items = [];
            $("nav#menus a.edit").each(function() {
                items = items.concat([{
                    "id": $(this).attr('data-id'),
                    "order": i
                }]);
                i++;
            });
            $.ajax({
                url: '/sherpa/cms/meny/sorter/',
                type: 'POST',
                data: 'menus=' + encodeURIComponent(JSON.stringify(items))
            }).fail(function(result) {
                // Todo
            }).always(function(result) {
                list.sortable('enable');
            });
        }
    });

    $("div.menu-dialog button.save-menu").click(function() {
        var name = $("div.menu-dialog input[name='name']").val();
        var url = $("div.menu-dialog input[name='url']").val();
        if(!url.match(/^https?:\/\//)) {
            url = "http://" + url;
        }
        var ajaxUrl;
        if(activeMenu === undefined) {
            ajaxUrl = 'ny/';
        } else {
            ajaxUrl = 'rediger/' + encodeURIComponent(activeMenu.attr('data-id')) + '/';
        }
        $.ajax({
            url: '/sherpa/cms/meny/' + ajaxUrl,
            type: 'POST',
            data: 'name=' + encodeURIComponent(name) +
                  '&url=' + encodeURIComponent(url)
        }).done(function(result) {
            if(activeMenu === undefined) {
                result = JSON.parse(result);
                var item = $('<li><a class="edit" data-id="' + result.id + '" data-href="' + url + '"  href="javascript:undefined">' + name + '</a></li>');
                item.find("a.edit").click(edit);
                $("nav#menus li").last().before(item);
            } else {
                activeMenu.text(name);
                activeMenu.attr('data-href', url);
            }
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            $("div.menu-dialog").dialog('close');
        });
    });

    $("div.menu-dialog button.delete-menu").click(function() {
        if(!confirm('Er du sikker på at du vil slette denne linken fra hovedmenyen?')) {
            return;
        }
        $.ajax({
            url: '/sherpa/cms/meny/slett/' + activeMenu.attr('data-id') + '/',
            type: 'POST'
        }).done(function(result) {
            activeMenu.remove();
        }).fail(function(result) {
            // Todo
        }).always(function(result) {
            $("div.menu-dialog").dialog('close');
        });
    });
});
