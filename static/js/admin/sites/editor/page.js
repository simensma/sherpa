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

    $(document).on('click', '.editor-header .actions .delete-page:not(.disabled)', function (e) {

        var modalOptions = {};

        var $editorHeader = $(this).parents('.editor-header').first();

        modalOptions.hasChildren = true;
        modalOptions.deleteUrl = $(this).data('dnt-delete-url');
        modalOptions.title = $editorHeader.find('input[name="title"]').first().val();

        Turistforeningen.setupDeletePageModal(modalOptions);

    });

    /* Enable select2 for changing parent */
    header.find("select[name='parent']").select2();

    /* Init Tooltips */
    header.find('.preview').tooltip();
    header.find('.delete-page.disabled').css('pointer-events', 'all').tooltip();
    header.find('.form-group.parent select[disabled]').parents('[data-toggle="tooltip"]').first().tooltip();
    header.find('.form-group.title input[disabled]').parents('[data-toggle="tooltip"]').first().tooltip();
    header.find('.form-group.slug input[disabled]').parents('[data-toggle="tooltip"]').first().tooltip();

    /* Toggle published state info */
    header.find('input[name="publish"]').on('change', function (e) {
        var $publish_toggle_form_group = header.find('.form-group.publish');
        var $alert_is_published = $publish_toggle_form_group.find('.alert-success');
        var $alert_is_unpublished = $publish_toggle_form_group.find('.alert-warning');

        if (this.checked) {
            $alert_is_published.removeClass('jq-hide');
            $alert_is_unpublished.addClass('jq-hide');

        } else {
            $alert_is_published.addClass('jq-hide');
            $alert_is_unpublished.removeClass('jq-hide');
        }
    });


});
