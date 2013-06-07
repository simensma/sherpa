$(document).ready(function() {
    var signup = $("div.aktivitet-signup");
    var login = signup.find("div.choice.login");
    var register = signup.find("div.choice.register");
    var simple_signup = signup.find("div.choice.simple-signup");

    login.click(function(e) {
        $(this).find("p.action a").get(0).click();
    });

    login.find("p.action a").click(function(e) {
        e.stopPropagation();
    });

    register.click(function() {
        $(this).addClass('active');
        $(this).find("p.action").hide();
        $(this).find("div.content").slideDown();
    });

    simple_signup.click(function() {
        $(this).addClass('active');
        $(this).find("p.action").hide();
        $(this).find("div.content").slideDown();
    });
});
