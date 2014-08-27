(function(UrlPicker, $, undefined ) {

    var url_picker;
    var choice_controls;
    var pick_choices;
    var pick_choice_elements;
    var page_select;
    var page_url;
    var article_select;
    var article_url;
    var forening_select;
    var forening_url;
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
        article_select = pick_choices.find('select[name="article"]');
        article_url = pick_choices.find('span[data-dnt-text="article-url"]');
        forening_select = pick_choices.find('select[name="forening"]');
        forening_url = pick_choices.find('span[data-dnt-text="forening-url"]');
        save_button = url_picker.find('[data-dnt-trigger="save-url"]');

        /* Define event listeners */

        choice_controls.find('input').change(changeUrlType);
        page_select.change(displayPageUrl);
        article_select.change(displayArticleUrl);
        forening_select.change(displayForeningUrl);
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

    function displayArticleUrl() {
        var url = $(this).find('option:selected').val();
        article_url.text(url);
    }

    function displayForeningUrl(e) {
        var url = e.val;
        if(url === '') {
            alert(
                forening_url.parent().attr('data-no-url-warning')
                .replace(/%s/, $(e.added.element).text().trim())
                .replace(/\\n/g, '\n')
            );
            var first_option_val = $(this).find('option').eq(1).val();
            forening_select.select2('val', first_option_val, true);
            return;
        }
        forening_url.text(url);
    }

    function saveUrl() {
        var pick_type = choice_controls.find('input:checked').attr('value');
        var pick_choices = pick_choice_elements.filter('[data-dnt-pick-choice="' + pick_type + '"]');

        if(pick_type === 'page') {
            callback({
                type: 'anchor',
                url: page_select.find('option:selected').val(),
            });
        } else if(pick_type === 'article') {
            callback({
                type: 'anchor',
                url: article_select.find('option:selected').val(),
            });
        } else if(pick_type === 'forening') {
            callback({
                type: 'anchor',
                url: forening_select.select2('val'),
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
