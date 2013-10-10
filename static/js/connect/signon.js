$(document).ready(function() {

    var loginpage = $("div.loginpage-wrapper");

    var registration = loginpage.find("div#registration.tab-pane");
    var choose_creation = registration.find("div.choose-creation");
    var registration_tab = loginpage.find("ul.nav li a[href='#registration']");
    var registration_form_wrapper = registration.find("div.registration-form-wrapper");
    var registration_form_nonmember_wrapper = registration.find("div.registration-form-nonmember-wrapper");

    choose_creation.find("a.member, a.nonmember").click(function() {
        choose_creation.find("hr").show();
        if($(this).is('.member')) {
            registration_form_nonmember_wrapper.hide();
            registration_form_wrapper.slideDown();
        } else if($(this).is('.nonmember')) {
            registration_form_wrapper.hide();
            registration_form_nonmember_wrapper.slideDown();
        }
    });

    $.fn.Hashtag('bind', 'ikkemedlem', {
        'match': function() {
            choose_creation.find("hr").show();
            registration_form_nonmember_wrapper.show();
            registration_tab.tab('show');
        }
    });

    // Note that this overwrites the bind in toggle-loginpage-tabs.js
    $.fn.Hashtag('bind', 'registrering', {
        'match': function() {
            choose_creation.find("hr").show();
            registration_form_wrapper.show();
            registration_tab.tab('show');
        }
    });

});
