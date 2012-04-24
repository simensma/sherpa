/* Editing an article (not its contents) */

$(document).ready(function() {

    /* Publish/unpublish */

    $("div.published:not([data-active])").hide();
    $("div.published button.publish").click(function() {
        if($("div.published.true[data-active]").length == 0) {
            if(!confirm("Er du sikker på at du vil publisere den aktive versjonen for denne artikkelen?")) {
                return;
            }
        } else {
            if(!confirm("Er du HELT sikker på at du vil trekke tilbake denne artikkelen? Den vil forsvinne fra nyhetsutlistingen, og ikke dukke opp som søkeresultat når en søker. Du bør ikke avpublisere en publisert artikkel med mindre du er HELT sikker.")) {
                return;
            }
        }
        var button = $(this);
        button.attr('disabled', true);
        $.ajax({
            url: '/sherpa/artikler/publiser/' + $(this).parents("div.edit-article-header").attr('data-id') + '/',
            type: 'POST'
        }).done(function() {
            var active = $("div.published[data-active]");
            var inactive = $("div.published:not([data-active])");
            active.removeAttr('data-active').hide();
            inactive.attr('data-active', true).show();
        }).always(function() {
            button.removeAttr('disabled');
        });
    });

    /* Save header meta-data */

    $("div.edit-article-header h2.title").click(editHeader);
    $("div.edit-article-header p.description").click(editHeader);

    function editHeader() {
        var title = $("div.edit-article-header h2.title");
        var description = $("div.edit-article-header span.description");
        var input = $('<table class="input"><tr><td><input type="text" name="title" value="' + title.text() + '"></td></tr><tr><td><textarea rows="3" name="description" class="span4">' + description.text() + '</textarea></td></tr><tr><td><button class="btn btn-success save-header"><i class="icon-ok"></i> Lagre</button></td></tr></table>');
        input.find("button").click(saveHeader);
        title.before(input).remove();
        description.parent().remove();
    }

    function saveHeader() {
        var title = $("div.edit-article-header input[name='title']").val();
        var description = $("div.edit-article-header textarea[name='description']").val();
        $.ajax({
            url: '/sherpa/artikler/rediger/' + $(this).parents("div.edit-article-header").attr('data-id') + '/',
            type: 'POST',
            data: 'title=' + encodeURIComponent(title) +
                  '&description=' + encodeURIComponent(description)
        }).done(function() {
            title = $('<h2 class="title">' + title + '</h2>');
            description = $('<p class="description"><i class="icon-pencil"></i> <span class="description">' + description + '</span></p>');
            $(title).click(editHeader);
            $(description).click(editHeader);
            $("div.edit-article-header table.input").before(title, description).remove();
            $("a.header-title").text(title.text());
        });
    }

    /* Change header-image */

    $("div.edit-article-header img.article-thumbnail").click(function() {
        var image = $(this);
        openImageDialog($(this).attr('src'), '', '', saveImage);
        function saveImage(url, anchor, alt) {
            $.ajax({
                url: '/sherpa/artikler/bilde/' + image.parents("div.edit-article-header").attr('data-id') + '/',
                type: 'POST',
                data: 'thumbnail=' + encodeURIComponent(url)
            }).done(function() {
                image.attr('src', url);
            });
        }
    });

});
