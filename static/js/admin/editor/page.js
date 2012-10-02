$(document).ready(function() {

    /* Publishing-time datetimepicker */
    $("div.editor-header.page div.publish input[name='page-datetime-field']").datetimepicker({
        dateFormat: "dd.mm.yy",
        seperator: " ",
        timeFormat: "hh:mm"
    });

    /* Delete page */
    $("div.editor-header.page a.delete-page").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne siden, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

    /* Rename title */
    $("div.editor-header.page input[name='title']").focusout(function() {
        var title = $(this).val();
        $("div.editor-header.page span.title-status").hide();
        $(this).after('<img class="title-loader" src="/static/img/ajax-loader-small.gif" alt="Laster...">');
        debugger;
        $.ajax({
            url: '/sherpa/cms/side/tittel/' + $("div.editor-header").attr('data-page-id') + '/',
            data: 'title=' + encodeURIComponent(title)
        }).always(function() {
            $("div.editor-header.page img.title-loader").remove();
            $("div.editor-header.page span.title-status").show();
        });
    });

    /* Change parent */
    $("div.editor-header.page select[name='parent']").change(function() {
        var parent = $(this).find("option:selected").val();
        $("div.editor-header.page span.parent-status").hide();
        $(this).after('<img class="parent-loader" src="/static/img/ajax-loader-small.gif" alt="Laster...">');
        $.ajax({
            url: '/sherpa/cms/side/foreldre/' + $("div.editor-header").attr('data-page-id') + '/',
            data: 'parent=' + encodeURIComponent(parent)
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.error == 'parent_in_parent') {
                alert('Du kan ikke velge den siden, fordi den allerede er en underside av denne siden.');
                $("div.editor-header.page select[name='parent']").val($("div.editor-header.page select[name='parent'] option.default").val());
            } else {
                $("div.editor-header.page select[name='parent'] option.default").removeClass('default');
                $("div.editor-header.page select[name='parent'] option:selected").addClass('default');
            }
        }).always(function() {
            $("div.editor-header.page img.parent-loader").remove();
            $("div.editor-header.page span.parent-status").show();
        });
    });

});
