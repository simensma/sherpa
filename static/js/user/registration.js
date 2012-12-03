$(document).ready(function() {

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

    Validator.validatePasswords({
        control_group: $("div.control-group.password, div.control-group.password-repeat"),
        pass1: $("input[name='password']"),
        pass2: $("input[name='password-repeat']"),
        min_length: user_password_length,
        hints: $("div.form-hints div.password-hint")
    });

    Validator.validate({
        method: 'memberid',
        control_group: $("div.control-group.memberid"),
        input: $("input[name='memberid']"),
        req: true
    });

    Validator.validateZipcode(
        $("div.control-group.zipcode"),
        $("input[name='zipcode']"),
        $("input[name='area']"),
        $("img.ajaxloader.zipcode")
    );

    var memberid_accepted = false;
    var no_memberid_match = $("div.form-hints div.no-memberid-match");
    $("form").submit(function(e) {
        if(memberid_accepted) {
            return $(this);
        }
        no_memberid_match.hide();
        e.preventDefault();
        var form = $(this);
        form.find("button[type='submit']").hide();
        form.find("img.ajaxloader.submit").show();
        $.ajax({
            url: '/minside/sjekk-medlemsnummer/',
            data: 'memberid=' + encodeURIComponent(form.find("input[name='memberid']").val()) +
                  '&zipcode=' + encodeURIComponent(form.find("input[name='zipcode']").val())
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.exists) {
                enableStep2(result);
            } else {
                no_memberid_match.find("span.memberid").text(form.find("input[name='memberid']").val());
                no_memberid_match.find("span.zipcode").text(form.find("input[name='zipcode']").val());
                no_memberid_match.slideDown();
                form.find("button.step1").show();
                form.find("img.ajaxloader.submit").hide();
            }
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            form.find("button[type='submit']").show();
            form.find("img.ajaxloader.submit").hide();
        });
    });

    function enableStep2(result) {
        memberid_accepted = true;
        $("div.form-elements div.step1 input").attr('disabled', true);
        $("div.form-elements div.step2").slideDown();

        $("div.form-hints div.step2 span.name").text(result.name);
        if(result.email != '') {
            $("div.form-hints div.step2 span.email-found").show().find("span.email").text(result.email);
        }
        $("div.form-elements div.step2 input[name='email']").val(result.email);
        $("button.step2").show();
        $("img.ajaxloader.submit").hide();
        $("div.form-hints div.step1").fadeOut(function() {
            // Wait for fadeOut to complete before fadeIn
            $("div.form-hints div.step2").fadeIn();
        });
    }

});
