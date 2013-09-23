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

    Validator.validate({
        method: 'full_name',
        control_group: simple_signup.find("div.control-group.name"),
        input: simple_signup.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: simple_signup.find("div.control-group.email"),
        input: simple_signup.find("input[name='email']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        control_group: simple_signup.find("div.control-group.phone"),
        input: simple_signup.find("input[name='phone']"),
        req: false
    });

    simple_signup.find("form.simple-signup").submit(function(e) {
        if($(this).find("input[name='email']").val().trim() === '' && $(this).find("input[name='phone']").val().trim() === '') {
            alert("Du må oppgi enten et telefonnummer eller en e-postadresse.");
            e.preventDefault();
        }
    });
});
