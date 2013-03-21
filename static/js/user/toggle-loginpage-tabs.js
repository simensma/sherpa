$(document).ready(function() {

    $.fn.Hashtag('bind', 'registrering', {
        'match': toggleRegistration
    });

    $("a.toggle-registration-tab").click(toggleRegistration);
    $("a.toggle-login-tab").click(toggleLogin);

    function toggleLogin() {
        $("ul.nav li a[href='#login']").tab('show');
    }

    function toggleRegistration() {
        $("ul.nav li a[href='#registration']").tab('show');
    }

});
