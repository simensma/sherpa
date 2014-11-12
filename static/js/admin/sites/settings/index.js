$(function() {

    var wrapper = $('[data-dnt-container="site-settings"]');

    var forening_select = wrapper.find('select[name="site_forening"]');

    var site_type_wrapper = wrapper.find('[data-dnt-form-group="type"]');
    var site_type_buttons = site_type_wrapper.find('input[name="type"]');
    var title_wrapper = wrapper.find('[data-dnt-form-group="title"]');
    var template_type_wrapper = wrapper.find('[data-dnt-form-group="template-type"]');
    var template_description_wrapper = wrapper.find('[data-dnt-form-group="template-description"]');

    forening_select.select2();

    site_type_buttons.change(function() {
        var checked = site_type_buttons.filter(':checked');
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
    });

});
