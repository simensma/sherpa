$(document).ready(function() {
    var signup = $("div.aktivitet-signup");
    var login = signup.find("div.choice.login");
    var register = signup.find("div.choice.register");
    var simple_signup = signup.find("div.choice.simple-signup");

    simple_signup.click(function() {
        $(this).find("p.action").hide();
        $(this).find("div.content").slideDown();
    });
});
