$(function() {

    /* DOM lookups */

    var wrapper = $("div.setup-site");

    var forening_select = wrapper.find('select[name="site_forening"]');

    var site_type_wrapper = wrapper.find('[data-dnt-form-group="type"]');
    var site_type_forening = site_type_wrapper.find('input[value="forening"]');
    var site_type_buttons = site_type_wrapper.find("input[name='type']");

    var title_wrapper = wrapper.find("div.form-group.title");
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
    site_type_buttons.change(chooseFormFields);
    domain_type.change(changeDomainType);
    submit.click(validateForm);

    /* Event implementations */

    function hideHomepageSite() {
        var forening_id = forening_select.val();
        if(Turistforeningen.foreninger_with_homepage[forening_id]) {
            site_type_forening.prop('checked', false);
            site_type_forening.prop('disabled', true);
        } else {
            site_type_forening.prop('disabled', false);
        }
    }

    function chooseFormFields() {
        var checked = site_type_buttons.filter(":checked");
        if(checked.val() === 'hytte' || checked.val() === 'kampanje') {
            title_wrapper.slideDown('fast');
            template_type_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
        } else if(checked.val() === 'mal') {
            title_wrapper.slideDown('fast');
            template_type_wrapper.slideDown('fast');
            template_description_wrapper.slideDown('fast');
        } else {
            title_wrapper.slideUp('fast');
            template_type_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
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
