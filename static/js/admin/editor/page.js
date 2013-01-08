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

    /* Change parent */
    $("div.editor-header.page select[name='parent']").chosen({
        'allow_single_deselect': true
    });

});
