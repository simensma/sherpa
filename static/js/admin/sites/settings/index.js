$(function() {

    var wrapper = $('[data-dnt-container="site-settings"]');

    var edited_site = wrapper.find('input[name="edited_site"]');
    var forening_select = wrapper.find('select[name="forening"]');

    var site_type_wrapper = wrapper.find('[data-dnt-form-group="type"]');
    var site_type_buttons = site_type_wrapper.find('input[name="type"]');
    var site_type_forening = site_type_wrapper.find('input[value="forening"]');
    var site_type_forening_info = site_type_wrapper.find('[data-dnt-container="has-homepage-info"]');
    var site_type_forening_info_name = site_type_forening_info.find('[data-dnt-container="forening-name"]');

    var title_wrapper = wrapper.find('[data-dnt-form-group="title"]');

    var template_type_wrapper = wrapper.find('[data-dnt-form-group="template-type"]');
    var template_main_wrapper = wrapper.find('[data-dnt-form-group="template-main"]');
    var template_description_wrapper = wrapper.find('[data-dnt-form-group="template-description"]');

    // Show/hide homepage type choice based on the default selected forening
    hideHomepageSite();

    forening_select.select2();
    forening_select.change(hideHomepageSite);
    site_type_buttons.change(setFormFields);

    function hideHomepageSite() {
        var current_site = edited_site.val();
        var homepage_id = forening_select.find('option:selected').attr('data-dnt-homepage');
        var has_homepage = homepage_id !== undefined;

        // Note if we're currently editing this forening's homepage, we should, of course, not disable the homepage
        // option
        if(has_homepage && homepage_id !== current_site) {
            site_type_forening.prop('checked', false);
            site_type_forening.prop('disabled', true);
            site_type_forening_info_name.text(forening_select.find('option:selected').text());
            site_type_forening_info.show();
        } else {
            site_type_forening.prop('disabled', false);
            site_type_forening_info.hide();
        }
    }

    function setFormFields() {
        var checked = site_type_buttons.filter(':checked');
        if(checked.val() === 'hytte' || checked.val() === 'kampanje') {
            title_wrapper.slideDown('fast');
            template_type_wrapper.slideUp('fast');
            template_main_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
        } else if(checked.val() === 'mal') {
            title_wrapper.slideDown('fast');
            template_type_wrapper.slideDown('fast');
            template_main_wrapper.slideDown('fast');
            template_description_wrapper.slideDown('fast');
        } else {
            title_wrapper.slideUp('fast');
            template_type_wrapper.slideUp('fast');
            template_main_wrapper.slideUp('fast');
            template_description_wrapper.slideUp('fast');
        }
    }

});
