$(function() {

    var wrapper = $('[data-dnt-container="admin-analytics-index"]');
    var analytics_ua_hint_trigger = wrapper.find('[data-dnt-trigger="analytics-ua-hint"]');
    var analytics_ua_hint_container = wrapper.find('[data-dnt-container="analytics-ua-hint"]');

    analytics_ua_hint_trigger.click(function() {
        analytics_ua_hint_container.slideToggle('slow');
    });

});
