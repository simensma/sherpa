(function(UrlPicker, $, undefined ) {

    var url_picker;
    var url_type_choices;
    var url_types;
    var save_button;

    $(function() {

        /* Look up elements */

        url_picker = $('[data-dnt-container="url-picker"]');
        url_types = url_picker.find('[data-dnt-container="url-type"]');
        url_type_choices = url_picker.find('[data-dnt-container="url-type-choices"]');
        save_button = url_picker.find('[data-dnt-trigger="save-url"]');

        /* Define event listeners */

        url_type_choices.find('input').change(function() {
            var url_type = url_type_choices.find('input:checked').attr('value');
            url_types.hide();
            url_types.filter('[data-dnt-url-type="' + url_type + '"]').slideDown('fast');
        });

    });

    /* Public functions */

    UrlPicker.open = function() {

        url_picker.modal();

    };

}(window.UrlPicker = window.UrlPicker || {}, jQuery ));
