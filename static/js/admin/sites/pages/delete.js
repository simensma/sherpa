/* Modal for deleting page and optionally its children */

$(function() {

    /* Setup delete page modal */

    Turistforeningen.setupDeletePageModal = function (options) {

        var $deletePageModal = $('div.modal.delete-page');

        $deletePageModal.find('[data-dnt-placeholder="page-title"]').html(options.title);
        $deletePageModal.find('[data-dnt-action="delete-page-keep-children"]').attr('href', options.deleteUrl);
        $deletePageModal.find('[data-dnt-action="delete-page-and-children"]').attr('href', options.deleteUrl + '?delete_children=true');

        $deletePageModal.modal();

        if (options.hasChildren) {
            $deletePageModal.addClass('has-children').removeClass('no-children');

        } else {
            $deletePageModal.addClass('no-children').removeClass('has-children');
        }
    };


    /* Click delete button in modal */

    $(document).on('click', 'div.modal.delete-page [data-dnt-action^="delete-page"]', function (e) {
        $('div.modal.delete-page [data-dnt-action^="delete-page"]').addClass('disabled');
        $(this).css('width', $(this).outerWidth()).html('Sletter...'); // Set the width to keep button size when replacing text.
    });

});
