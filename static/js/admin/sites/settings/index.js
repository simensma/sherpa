$(function() {

    var wrapper = $('[data-dnt-container="site-settings"]');

    var site_type_wrapper = wrapper.find('[data-dnt-form-group="type"]');
    var site_type_buttons = site_type_wrapper.find('input[name="type"]');
    var title_wrapper = wrapper.find('[data-dnt-form-group="title"]');

    site_type_buttons.change(function() {
        var checked = site_type_buttons.filter(':checked');
        if(checked.is('[value="hytte"]') || checked.is('[value="kampanje"]')) {
            title_wrapper.slideDown('fast');
        } else {
            title_wrapper.slideUp('fast');
        }
    });

});
