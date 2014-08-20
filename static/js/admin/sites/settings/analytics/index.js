$(function() {

    var wrapper = $('[data-dnt-container="admin-analytics-index"]');

    var analytics_ua_hint_trigger = wrapper.find('[data-dnt-trigger="analytics-ua-hint"]');
    var analytics_ua_hint_container = wrapper.find('[data-dnt-container="analytics-ua-hint"]');

    var analytics_ua_form_trigger = wrapper.find('[data-dnt-trigger="show-ua-form"]');
    var analytics_ua_form_container = wrapper.find('[data-dnt-container="analytics-ua-form"]');
    var analytics_ua_exists_container = wrapper.find('[data-dnt-container="ua-exists-block"]');

    analytics_ua_hint_trigger.click(function() {
        analytics_ua_hint_container.slideToggle('slow');
    });

    analytics_ua_form_trigger.click(function() {
        analytics_ua_exists_container.hide();
        analytics_ua_form_container.show();
    });

});
