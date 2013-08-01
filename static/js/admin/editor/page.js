$(document).ready(function() {

    var header = $("div.editor-header.page");

    /* Publishing-time datetimepicker */
    header.find("div.publish input[name='page-datetime-field']").datetimepicker({
        dateFormat: "dd.mm.yy",
        seperator: " ",
        timeFormat: "hh:mm"
    });

    /* Delete page */
    header.find("a.delete-page").click(function(e) {
        if(!confirm("Er du HELT sikker på at du vil slette denne siden, for alltid?\n\nHvis du bare vil ta den bort fra forsiden og søkeresultater, men beholde innholdet, bør du heller bare avpublisere den.\n\nDette kan du ikke angre!")) {
            e.preventDefault();
        }
    });

    /* Change parent */
    header.find("select[name='parent']").chosen({
        'allow_single_deselect': true
    });

});
