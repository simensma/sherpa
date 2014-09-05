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
    var custom_input;
    var email_input;

    var forening_url;
    var save_button;
    var cancel_button;

    var callback;
    var cancel_callback;

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
        custom_input = pick_choices.find('input[name="custom"]');
        email_input = pick_choices.find('input[name="email"]');

        save_button = url_picker.find('[data-dnt-trigger="save-url"]');
        cancel_button = url_picker.find('[data-dnt-trigger="cancel"]');

        /* Define event listeners */

        choice_controls.find('input').change(changeUrlType);
        page_select.change(displayPageUrl);
        article_select.change(displayArticleUrl);
        forening_select.change(displayForeningUrl);
        save_button.click(saveUrl);
        cancel_button.click(cancel);

        // Trigger save on enter keypress in text inputs
        pick_choices.find('input[name="url"],input[name="email"]').keyup(function(e) {
            if(e.which == 13) { // Enter
                save_button.click();
            }
        });

        /* Initiate custom controls */

        url_picker.find('select').select2();

    });

    /* Public functions */

    UrlPicker.open = function(opts) {

        callback = opts.done;
        cancel_callback = opts.cancel;
        url_picker.modal();

        if(opts.disable_email !== true) {
            choice_controls.find('[data-dnt-choice="email"]').show();
        } else {
            choice_controls.find('[data-dnt-choice="email"]').hide();
        }

        // Reset control state
        choice_controls.find('input').prop('checked', false);
        pick_choice_elements.hide();

        // If an existing URL is specified, try to figure out what kind of lookup might have been used.
        if(opts.existing_url !== undefined && opts.existing_url !== '') {

            // Is it an email address? Note that we'll skip this step if disable_email is true
            if(opts.existing_url.startsWith('mailto:') && !opts.disable_email) {
                choice_controls.find('input[value="email"]').click();
                email_input.val(opts.existing_url.substring("mailto:".length));
                return;
            }

            // Search through page URLs
            var existing_option = page_select.find('option[value="' + opts.existing_url + '"]');
            if(existing_option.length > 0) {
                choice_controls.find('input[value="page"]').click();
                page_select.select2('val', existing_option.val(), true);
                return;
            }

            // Search through article URLs
            existing_option = article_select.find('option[value="' + opts.existing_url + '"]');
            if(existing_option.length > 0) {
                choice_controls.find('input[value="article"]').click();
                article_select.select2('val', existing_option.val(), true);
                return;
            }

            // Search through foreninger
            existing_option = forening_select.find('option[value="' + opts.existing_url + '"]');
            if(existing_option.length > 0) {
                choice_controls.find('input[value="forening"]').click();
                forening_select.select2('val', existing_option.val(), true);
                return;
            }

            // Looks like none of the lookup URLs matched - fall back to custom URL
            choice_controls.find('input[value="custom"]').click();
            custom_input.val(opts.existing_url);
            return;
        }
        // Note that the above statement returns; if you want to add code here, rewrite the above if-statement.
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
        var pick_choice = pick_choice_elements.filter('[data-dnt-pick-choice="' + pick_type + '"]');

        if(pick_type === 'page') {
            callback({
                type: 'anchor',
                url: page_select.find('option:selected').val(),
            });
        } else if(pick_type === 'article') {
            var selected = article_select.find('option:selected');
            if(selected.length === 0) {
                alert(pick_choices.attr('data-dnt-no-articles-warning'));
                return;
            }
            callback({
                type: 'anchor',
                url: selected.val(),
            });
        } else if(pick_type === 'forening') {
            callback({
                type: 'anchor',
                url: forening_select.select2('val'),
            });
        } else if(pick_type === 'custom') {
            var url = custom_input.val().trim();
            if(!url.startsWith('http://')) {
                alert(pick_choices.attr('data-dnt-invalid-url-warning').replace(/\\n/g, '\n'));
                return;
            }

            callback({
                type: 'anchor',
                url: url,
            });
        } else if(pick_type === 'email') {
            var email = email_input.val().trim();
            if(!Validator.check['email'](email, true)) {
                alert(pick_choices.attr('data-dnt-invalid-email-warning'));
                return;
            }

            callback({
                type: 'email',
                url: email,
            });
        } else {
            if(typeof(_cancel_callback) === 'function') {
                cancel_callback();
            }
        }
        url_picker.modal('hide');
    }

    function cancel() {
        if(typeof(_cancel_callback) === 'function') {
            cancel_callback();
        }
        url_picker.modal('hide');
    }

}(window.UrlPicker = window.UrlPicker || {}, jQuery ));
