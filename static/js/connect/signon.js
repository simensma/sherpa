$(document).ready(function() {

    var loginpage = $("div.loginpage-wrapper");

    var registration = loginpage.find("div#registration.tab-pane");
    var choose_creation = registration.find("div.choose-creation");
    var registration_tab = loginpage.find("ul.nav li a[href='#registration']");
    var registration_form_wrapper = registration.find("div.registration-form-wrapper");
    var registration_form_nonmember_wrapper = registration.find("div.registration-form-nonmember-wrapper");

    choose_creation.find("a.member, a.nonmember").click(function() {
        var complete;
        if($(this).is('.member')) {
            complete = function() {
                registration_form_wrapper.fadeIn(200);
            };
        } else if($(this).is('.nonmember')) {
            complete = function() {
                registration_form_nonmember_wrapper.fadeIn(200);
            };
        }
        choose_creation.fadeOut(200, complete);
    });

    $.fn.Hashtag('bind', 'ikkemedlem', {
        'match': function() {
            choose_creation.hide();
            registration_form_nonmember_wrapper.show();
            registration_tab.tab('show');
        }
    });

    // Note that this overwrites the bind in toggle-loginpage-tabs.js
    $.fn.Hashtag('bind', 'registrering', {
        'match': function() {
            choose_creation.hide();
            registration_form_wrapper.show();
            registration_tab.tab('show');
        }
    });

});
