/* Editing a page (not its contents) */

$(document).ready(function() {

    /* New page dialog - define slug based on title */

    var validUrl = false;

    $("a.open-page-dialog").click(function() {
        $("div.page-dialog input[name='title']").keyup()
    });
    $("div.page-dialog img.loader").hide();
    $("div.page-dialog span.valid").hide();
    $("div.page-dialog span.invalid").hide();
    $("div.page-dialog input[name='title']").keyup(function() {
        lookupVal = $(this).val().replace(/[^-_a-z0-9\s]+/gi, '')
                                 .replace(/\s+/g, "-")
                                 .toLowerCase();
        updateSlash(lookupVal.length == 0);
        $("div.page-dialog span.slug").text(lookupVal);
        initiateLookup();
        clearTimeout(lookupTimer);
        lookupTimer = setTimeout(performLookup, KEY_LOOKUP_DELAY);
    });

    var lookupTimer;
    var lookupVal;
    var KEY_LOOKUP_DELAY = 1000;

    function initiateLookup() {
        $("div.page-dialog span.valid").hide();
        $("div.page-dialog span.invalid").hide();
        $("div.page-dialog img.loader").show();
    }

    function performLookup() {
        // Check dynamically that the slug is unique
        $.ajax({
            url: '/sherpa/cms/side/ny/unik/',
            data: 'slug=' + encodeURIComponent(lookupVal)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.valid) {
                validUrl = true;
                $("div.page-dialog span.valid").show();
            } else {
                validUrl = false;
                $("div.page-dialog span.invalid").show();
            }
        }).fail(function(result) {
            // Todo
        }).always(function() {
            $("div.page-dialog img.loader").hide();
        });
    }

    $("div.page-dialog i.save-slug").hide().click(saveSlug);
    $("div.page-dialog i.edit-slug").click(editSlug);
    $("div.page-dialog span.slug").click(editSlug);

    function editSlug() {
        $("div.page-dialog i.edit-slug").hide();
        $("div.page-dialog i.save-slug").show();
        var span = $("div.page-dialog span.slug");
        var input = $('<input type="text" name="slug-input" value="' + decodeURIComponent(span.text()) + '">');
        input.focusout(saveSlug);
        input.keyup(function() {
            lookupVal = encodeURIComponent($(this).val()).replace('%2F', '/');
            initiateLookup();
            clearTimeout(lookupTimer);
            lookupTimer = setTimeout(performLookup, KEY_LOOKUP_DELAY);
        });
        span.before(input);
        span.remove();
        input.focus();
    }

    function saveSlug() {
        var input = $("div.page-dialog input[name='slug-input']");
        var val = input.val();
        val = val.replace(/\/+$/, '');
        updateSlash(val.length == 0);
        var span = $('<span class="slug">' + encodeURIComponent(val).replace('%2F', '/') + '</span>');
        input.before(span);
        input.remove();
        lookupVal = val;
        initiateLookup();
        performLookup();
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

    $("div.page-dialog img[data-template]").click(function() {
        if(!validUrl) {
            alert("URLen du valgte er allerede i bruk av en annen side! Vennligst velg en annen URL.");
            return;
        }
        if($("div.page-dialog input[name='title']").val().length == 0) {
            alert("Du må skrive inn en tittel på siden før du oppretter den!");
            return;
        }
        $("div.page-dialog input[name='template']").val($(this).attr('data-template'));
        $(this).parents("form").submit();
    });

    /* Expanding page-hierarchy */

    $(document).on('click', 'a.expand', function() {
        var i = $(this).children("i");
        if(i.hasClass('icon-plus')) {
            i.removeClass('icon-plus');
            i.addClass('icon-minus');
            var tr = $(this).parents("tr");
            var level = Number($(this).parents("td").attr('data-level')) + 1;
            var id = $(this).attr("data-id");
            var loader = '<tr class="loader"><td colspan="2"><img src="/static/img/ajax-loader-small.gif" alt="Laster..."></td></tr>';
            $(this).parents("tr").after(loader);
            $.ajax({
                url: '/sherpa/cms/side/barn/' + id + '/',
                data: 'level='+ encodeURIComponent(level)
            }).done(function(result) {
                $("table.pages tr.loader").remove();
                tr.after(result);
                updateLevels();
            });
        } else {
            i.addClass('icon-plus');
            i.removeClass('icon-minus');
            removeChildren($(this).parents('tr'));
        }
    });

    function removeChildren(tr) {
        var children = $("table.pages tr[data-parent='" + tr.attr('data-id') + "']");
        children.each(function() {
            removeChildren($(this));
        });
        children.remove();
    }

    updateLevels();
    function updateLevels() {
        var indent = 24;
        $("table.pages td[data-level]").each(function() {
            var css = indent * Number($(this).attr('data-level')) + "px";
            $(this).css('padding-left', css);
        });
    }

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
