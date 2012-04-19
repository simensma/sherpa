/* Editing a page (not its contents) */

$(document).ready(function() {

    $("table#page-details img.ajaxloader").hide();
    $("table#page-details input[name='title']").change(updatePage);
    $("table#page-details input[name='slug']").change(updatePage);

    function updatePage() {
        var table = $("table#page-details");
        var id = table.attr('data-id');
        var title = table.find("input[name='title']");
        var slug = table.find("input[name='slug']");
        title.attr('disabled', true);
        slug.attr('disabled', true);
        table.find("img.ajaxloader").show();
        $.ajax({
            url: '/sherpa/cms/side/' + id + '/',
            type: 'POST',
            data: 'title=' + encodeURIComponent(title.val()) +
                  '&slug=' + encodeURIComponent(slug.val())
        }).done(function(result) {

        }).fail(function(result) {
            // Todo
        }).always(function() {
            table.find("img.ajaxloader").hide();
            $("span.title").text(title.val());
            title.attr('disabled', false);
            slug.attr('disabled', false);
        });
    }

    $("table#page-details a.delete-page").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette hele denne siden, alle dens versjoner og varianter, og alt dens innhold FOR GODT? Denne handlingen kan du ikke angre!")) {
            e.preventDefault();
        }
    });

    /* New page dialog - define slug based on title */

    $("div.page-dialog input[name='title']").keyup(function() {
        var val = $(this).val();
        val = val.replace(/[^-_a-z0-9\s]+/gi, '')
                 .replace(/\s+/g, "-")
                 .toLowerCase();
        updateSlash(val.length == 0);
        $("div.page-dialog span.slug").text(val);
    });

    $("div.page-dialog i.save-slug").hide().click(saveSlug);
    $("div.page-dialog i.edit-slug").click(editSlug);
    $("div.page-dialog span.slug").click(editSlug);

    function editSlug() {
        $("div.page-dialog i.edit-slug").hide();
        $("div.page-dialog i.save-slug").show();
        var span = $("div.page-dialog span.slug");
        var input = $('<input type="text" name="slug" value="' + decodeURIComponent(span.text()) + '">');
        input.focusout(saveSlug);
        span.before(input);
        span.remove();
        input.focus();
    }

    function saveSlug() {
        var input = $("div.page-dialog input[name='slug']");
        var val = input.val();
        val = val.replace(/\/+$/, '');
        updateSlash(val.length == 0);
        var span = $('<span class="slug">' + encodeURIComponent(val) + '</span>');
        input.before(span);
        input.remove();
        $("div.page-dialog i.save-slug").hide();
        $("div.page-dialog i.edit-slug").show();
    }

    function updateSlash(hide) {
        if(hide) {
            $("div.page-dialog span.slash").text('');
        } else {
            $("div.page-dialog span.slash").text('/');
        }
    }

    $("div.page-dialog form").submit(function() {
        $(this).find("input[name='slug']").val($(this).find("span.slug").text());
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
