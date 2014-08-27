(function(UrlPicker, $, undefined ) {

    var url_picker;
    var url_type_choices;
    var url_types;
    var save_button;

    var callback;

    $(function() {

        /* Look up elements */

        url_picker = $('[data-dnt-container="url-picker"]');
        url_types = url_picker.find('[data-dnt-container="url-type"]');
        url_type_choices = url_picker.find('[data-dnt-container="url-type-choices"]');
        save_button = url_picker.find('[data-dnt-trigger="save-url"]');

        /* Define event listeners */

        url_type_choices.find('input').change(changeUrlType);
        save_button.click(saveUrl);

    });

    /* Public functions */

    UrlPicker.open = function(_callback) {

        callback = _callback;
        url_picker.modal();

    };

    /* Private functions */

    function changeUrlType() {
        var url_type = url_type_choices.find('input:checked').attr('value');
        url_types.hide();
        url_types.filter('[data-dnt-url-type="' + url_type + '"]').slideDown('fast');
    }

    function saveUrl() {
        var url_type = url_type_choices.find('input:checked').attr('value');
        var url_type_wrapper = url_types.filter('[data-dnt-url-type="' + url_type + '"]');

        if(url_type === 'email') {
            callback({
                type: 'email',
                url: url_type_wrapper.find('input[name="email"]').val(),
            });
        }
        url_picker.modal('hide');
    }

}(window.UrlPicker = window.UrlPicker || {}, jQuery ));
