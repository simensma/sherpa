$(function() {

    var header = $("div.editor-header.page");

    /* Publishing-time datepicker */
    header.find("div.publish div.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    });


    /* Delete page from editor */

    $(document).on('click', '.editor-header .actions .delete-page', function (e) {

        var modalOptions = {};

        var $editorHeader = $(this).parents('.editor-header').first();

        modalOptions.hasChildren = true;
        modalOptions.deleteUrl = $(this).data('dnt-delete-url');
        modalOptions.title = $editorHeader.find('input[name="title"]').first().val();

        Turistforeningen.setupDeletePageModal(modalOptions);

    });


    /* Change parent */
    header.find("select[name='parent']").chosen({
        'allow_single_deselect': true
    });

    // Init Tooltip
    header.find('.preview').tooltip();

});
