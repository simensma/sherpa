$(function() {

    /* DOM lookups */

    var wrapper = $("div.setup-site");

    var forening_select = wrapper.find('select[name="site_forening"]');

    var site_type_wrapper = wrapper.find('[data-dnt-form-group="type"]');
    var site_type_forening = site_type_wrapper.find('input[value="forening"]');
    var site_type_forening_info = site_type_wrapper.find('[data-dnt-container="has-homepage-info"]');
    var site_type_forening_info_name = site_type_forening_info.find('[data-dnt-container="forening-name"]');
    var site_type_buttons = site_type_wrapper.find("input[name='type']");

    var title_wrapper = wrapper.find("div.form-group.title");
    var template_wrapper = wrapper.find('[data-dnt-form-group="template"]');

    var default_template = wrapper.find('[data-dnt-container="default-template"]');
    var choose_template_trigger = wrapper.find('[data-dnt-trigger="choose-template"]');
    var choose_template = wrapper.find('[data-dnt-container="choose-template"]');
    var template_missing_checkbox = template_wrapper.find('input[name="template"][value=""]');
    var missing_template_type = template_wrapper.find('input[name="missing-template-type"]');

    var template_type_wrapper = wrapper.find('[data-dnt-form-group="template-type"]');
    var template_description_wrapper = wrapper.find('[data-dnt-form-group="template-description"]');

    var domain_wrapper = wrapper.find("div.form-group.domain");
    var domain = domain_wrapper.find("input[name='domain']");
    var domain_type = domain_wrapper.find("input[name='domain-type']");
    var subdomain_tail = domain_wrapper.find("span.subdomain-tail");

    var submit = wrapper.find("button[type='submit']");

    // Show/hide homepage type choice based on the default selected forening
    hideHomepageSite();

    /* Bind events */

    forening_select.select2();
    forening_select.change(hideHomepageSite);
    forening_select.change(setDefaultTemplate);
    site_type_buttons.change(chooseFormFields);
    site_type_buttons.change(setDefaultTemplate);
    choose_template_trigger.click(chooseTemplateManually);
    domain_type.change(changeDomainType);
    submit.click(validateForm);

    /* Event implementations */

    function hideHomepageSite() {
        var forening_id = forening_select.val();
        if(Turistforeningen.foreninger_with_homepage[forening_id]) {
            site_type_forening.prop('checked', false);
            site_type_forening.prop('disabled', true);
            site_type_forening_info_name.text(forening_select.find('option:selected').text());
            site_type_forening_info.show();
        } else {
            site_type_forening.prop('disabled', false);
            site_type_forening_info.hide();
        }
    }

    function setDefaultTemplate() {
        var site_type = site_type_buttons.filter(':checked').val();
        var forening_type = forening_select.find('option:selected').attr('data-dnt-type');
        var template_type;

        // Figure out what template type we should default to
        if(site_type === 'forening') {
            if(forening_type === 'sentral' || forening_type === 'forening') {
                template_type = 'forening';
            } else {
                template_type = 'turlag';
            }
        } else if(site_type === 'hytte') {
            template_type = 'hytte';
        } else if(site_type === 'kampanje') {
            template_type = 'kampanje';
        } else if(site_type === 'mal') {
            // The template type will not be used when creating a template site, so just return
            return;
        }

        var chosen_template_input = template_wrapper.find('input[name="template"][data-dnt-template-type="' + template_type + '"]');
        if(chosen_template_input.length === 0) {
            // What!? The template doesn't exist. This is a sherpa-admin user error. Check the template-missing
            // checkbox so we can handle it server-side.
            template_missing_checkbox.prop('checked', true);
            missing_template_type.val(template_type);
        } else {
            chosen_template_input.prop('checked', true);
        }
    }

    function chooseTemplateManually() {
        default_template.hide();
        choose_template.slideDown('fast');
    }

    function chooseFormFields() {
        var checked = site_type_buttons.filter(":checked");
        if(checked.val() === 'forening') {
            title_wrapper.slideUp('fast');
            template_wrapper.slideDown('fast');
            template_type_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
        } else if(checked.val() === 'hytte' || checked.val() === 'kampanje') {
            title_wrapper.slideDown('fast');
            template_wrapper.slideDown('fast');
            template_type_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
        } else if(checked.val() === 'mal') {
            title_wrapper.slideDown('fast');
            template_wrapper.slideUp('fast');
            template_type_wrapper.slideDown('fast');
            template_description_wrapper.slideDown('fast');
        }
    }

    function changeDomainType() {
        if(domain_type.filter(":checked").is("[value='subdomain']")) {
            domain.removeClass('fqdn');
            subdomain_tail.show();
        } else {
            domain.addClass('fqdn');
            subdomain_tail.hide();
        }
    }

    function validateForm(e) {
        if(site_type_buttons.filter(":checked").length === 0) {
            alert(submit.attr('data-choose-site-type-warning'));
            e.preventDefault();
            return;
        }
        if(domain.val().trim() === 'forening' || domain.val().trim() === '') {
            alert(submit.attr('data-enter-domain-warning'));
            e.preventDefault();
            return;
        }
    }

});
