$(document).ready(function() {

    var wrapper = $("div.loginpage-wrapper");

    $.fn.Hashtag('bind', 'registrering', {
        'match': toggleRegistration
    });

    wrapper.find("a.toggle-registration-tab").click(toggleRegistration);
    wrapper.find("a.toggle-login-tab").click(toggleLogin);

    function toggleLogin() {
        wrapper.find("ul.nav li a[href='#login']").tab('show');
    }

    function toggleRegistration() {
        wrapper.find("ul.nav li a[href='#registration']").tab('show');
    }

});
