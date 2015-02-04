(function(FileUploader, $, undefined ) {

    var file_uploader;
    var file_url;

    var save_button;
    var cancel_button;

    var callback;
    var cancel_callback;

    $(function() {

        /* Look up elements */

        file_uploader = $('[data-dnt-container="file-uploader"]');

        section_select_file = file_uploader.find('.section.select-file');
        browse_button = file_uploader.find('.fileinput-button');
        section_uploading_file = file_uploader.find('.section.uploading-file');
        success_msg = file_uploader.find('.section.status-message .success');
        error_msg = file_uploader.find('.section.status-message .error');
        existing_msg = file_uploader.find('.section.status-message .existing');
        save_button = file_uploader.find('[data-dnt-trigger="insert-file"]');
        cancel_button = file_uploader.find('[data-dnt-trigger="cancel"]');


        /* Define event listeners */

        save_button.click(insertLink);
        cancel_button.click(cancel);


        /* Initiate custom controls */
        file_uploader.find('[data-dnt-fileupload]').fileupload({
            dataType: 'json',
            always: function (e, data) {
                section_uploading_file.hide();
                save_button.attr('disabled', false);
            },
            done: function (e, data) {
                // Get file URL from arguments returned from server
                file_url = data.result.files[0].url;
                success_msg.show();
            },
            fail: function (e, data) {
                browse_button.show();
                error_msg.show();
            }
        }).bind('fileuploadstart', function (e) {
            success_msg.hide();
            error_msg.hide();
            section_select_file.hide();
            section_uploading_file.show();
        });

    });

    /* Public functions */

    FileUploader.open = function(opts) {

        callback = opts.done;
        cancel_callback = opts.cancel;
        file_uploader.modal();

        // Reset control state
        section_select_file.show();
        existing_msg.hide();
        success_msg.hide();
        error_msg.hide();
        save_button.attr('disabled', true);

        if (opts.existing_url) {
            file_uploader.find('[data-dnt-placeholder="existing-text"]').text(opts.existing_text);
            file_uploader.find('[data-dnt-placeholder="existing-url"]').text(opts.existing_url);
            existing_msg.show();
        }

    };

    /* Private functions */

    function insertLink() {
        callback({
            type: 'anchor',
            url: file_url
        });
        file_uploader.modal('hide');
    }

    function cancel() {
        if (typeof cancel_callback === 'function') {
            cancel_callback();
        }
        file_uploader.modal('hide');
    }

}(window.FileUploader = window.FileUploader || {}, jQuery ));
