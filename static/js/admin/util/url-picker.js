(function(UrlPicker, $, undefined ) {

    var url_picker;
    var choice_controls;
    var pick_choices;
    var pick_choice_elements;
    var page_select;
    var page_url;
    var save_button;

    var callback;

    $(function() {

        /* Look up elements */

        url_picker = $('[data-dnt-container="url-picker"]');
        choice_controls = url_picker.find('[data-dnt-container="choices"]');
        pick_choices = url_picker.find('[data-dnt-container="pick-choices"]');
        pick_choice_elements = url_picker.find('[data-dnt-container="pick-choice"]');
        page_select = pick_choices.find('select[name="page"]');
        page_url = pick_choices.find('span[data-dnt-text="page-url"]');
        save_button = url_picker.find('[data-dnt-trigger="save-url"]');

        /* Define event listeners */

        choice_controls.find('input').change(changeUrlType);
        page_select.change(displayPageUrl);
        save_button.click(saveUrl);

        /* Initiate custom controls */

        url_picker.find('select').select2();

    });

    /* Public functions */

    UrlPicker.open = function(_callback) {

        callback = _callback;
        url_picker.modal();

    };

    /* Private functions */

    function changeUrlType() {
        var pick_type = choice_controls.find('input:checked').attr('value');
        pick_choice_elements.hide();
        pick_choice_elements.filter('[data-dnt-pick-choice="' + pick_type + '"]').slideDown('fast');
    }

    function displayPageUrl() {
        var url = $(this).find('option:selected').val();
        page_url.text(url);
    }

    function saveUrl() {
        var pick_type = choice_controls.find('input:checked').attr('value');
        var pick_choices = pick_choice_elements.filter('[data-dnt-pick-choice="' + pick_type + '"]');

        if(pick_type === 'page') {
            callback({
                type: 'anchor',
                url: page_select.find('option:selected').val(),
            });
        } else if(pick_type === 'email') {
            callback({
                type: 'email',
                url: pick_choices.find('input[name="email"]').val(),
            });
        }
        url_picker.modal('hide');
    }

}(window.UrlPicker = window.UrlPicker || {}, jQuery ));
