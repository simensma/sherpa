/* Editing a page (not its contents) */

$(function() {

    /* New page dialog - define slug based on title */

    var validUrl = false;

    var newPage = $("div.new-page");

    $("a.new-page").click(function() {
        newPage.find("input[name='title']").keyup();
        newPage.modal();
    });
    newPage.find("img.loader").hide();
    newPage.find("span.valid").hide();
    newPage.find("span.invalid").hide();
    newPage.find("input[name='title']").keyup(function() {
        lookupVal = $(this).val().replace(/[^-_a-z0-9\s]+/gi, '')
                                 .replace(/\s+/g, "-")
                                 .toLowerCase();
        updateSlash(lookupVal.length == 0);
        newPage.find("span.slug").text(lookupVal);
        initiateLookup();
        clearTimeout(lookupTimer);
        lookupTimer = setTimeout(performLookup, KEY_LOOKUP_DELAY);
    });

    var lookupTimer;
    var lookupVal;
    var KEY_LOOKUP_DELAY = 1000;

    function initiateLookup() {
        newPage.find("span.valid").hide();
        newPage.find("span.invalid").hide();
        newPage.find("img.loader").show();
    }

    function performLookup() {
        // Check dynamically that the slug is unique
        $.ajaxQueue({
            url: newPage.attr('data-check-slug-url'),
            data: 'slug=' + encodeURIComponent(lookupVal)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.valid) {
                validUrl = true;
                newPage.find("span.valid").show();
            } else {
                validUrl = false;
                newPage.find("span.invalid").show();
            }
        }).fail(function(result) {
            // Todo
        }).always(function() {
            newPage.find("img.loader").hide();
        });
    }

    newPage.find("i.save-slug").hide().click(saveSlug);
    newPage.find("i.edit-slug").click(editSlug);
    newPage.find("span.slug").click(editSlug);

    function editSlug() {
        newPage.find("i.edit-slug").hide();
        newPage.find("i.save-slug").show();
        var span = newPage.find("span.slug");
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
        var input = newPage.find("input[name='slug-input']");
        var val = input.val();
        val = val.replace(/\/+$/, '');
        updateSlash(val.length == 0);
        var span = $('<span class="slug">' + encodeURIComponent(val).replace('%2F', '/') + '</span>');
        input.before(span);
        input.remove();
        lookupVal = val;
        initiateLookup();
        performLookup();
        newPage.find("i.save-slug").hide();
        newPage.find("i.edit-slug").show();
    }

    function updateSlash(hide) {
        if(hide) {
            newPage.find("span.slash").text('');
        } else {
            newPage.find("span.slash").text('/');
        }
    }

    newPage.find("form").submit(function() {
        $(this).find("input[name='slug']").val($(this).find("span.slug").text());
    });

    newPage.find("img[data-template]").click(function() {
        if(!validUrl) {
            alert("URLen du valgte er allerede i bruk av en annen side! Vennligst velg en annen URL.");
            return;
        }
        if(newPage.find("input[name='title']").val().length == 0) {
            alert("Du må skrive inn en tittel på siden før du oppretter den!");
            return;
        }
        newPage.find("input[name='template']").val($(this).attr('data-template'));
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
            $.ajaxQueue({
                url: '/sherpa/cms/side/barn/' + id + '/',
                data: { level: level }
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
