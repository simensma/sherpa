$(document).ready(function() {

    var memberid_accepted = false;
    var no_memberid_match = $("div.no-memberid-match");
    var registration_form = $("div.registration-form-wrapper form");

    Validator.validate({
        method: 'email',
        control_group: registration_form.find("div.control-group.email"),
        input: registration_form.find("input[name='email']"),
        req: true
    });

    Validator.validatePasswords({
        control_group: registration_form.find("div.control-group.password, div.control-group.password-repeat"),
        pass1: registration_form.find("input[name='password']"),
        pass2: registration_form.find("input[name='password-repeat']"),
        min_length: user_password_length,
        hints: registration_form.find("div.control-group.password div.controls div.hints.validator")
    });

    Validator.validate({
        method: 'memberid',
        control_group: registration_form.find("div.control-group.memberid"),
        input: registration_form.find("input[name='memberid']"),
        req: true
    });

    Validator.validateZipcode(
        $("div.control-group.zipcode"),
        $("input[name='zipcode']"),
        $("input[name='area']"),
        $("img.ajaxloader.zipcode")
    );

    registration_form.submit(function(e) {
        if(memberid_accepted) {
            return $(this);
        }
        no_memberid_match.hide();
        e.preventDefault();
        step1.find("button[type='submit']").hide();
        registration_form.find("img.ajaxloader.submit").show();
        $.ajax({
            url: '/minside/sjekk-medlemsnummer/',
            data: {
                memberid: registration_form.find("input[name='memberid']").val(),
                zipcode: registration_form.find("input[name='zipcode']").val()
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.exists) {
                if(!result.profile_exists) {
                    enableStep2(result);
                } else {
                    $("img.ajaxloader.submit").hide();
                    $("div.profile-exists").slideDown();
                }
            } else if(result.memberid_lookups_exceeded) {
                registration_form.find("img.ajaxloader.submit").hide();
                $("div.memberid-lookups-exceeded").slideDown();
            } else {
                no_memberid_match.find("span.memberid").text(registration_form.find("input[name='memberid']").val());
                no_memberid_match.find("span.zipcode").text(registration_form.find("input[name='zipcode']").val());
                no_memberid_match.slideDown();
                step1.find("button[type='submit']").show();
                registration_form.find("img.ajaxloader.submit").hide();
            }
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            step1.find("button[type='submit']").show();
            registration_form.find("img.ajaxloader.submit").hide();
        });
    });

    var step1 = registration_form.find("div.step1");
    var step2 = registration_form.find("div.step2");

    function enableStep2(result) {
        memberid_accepted = true;

        step2.find("span.name").text(result.name);
        if(result.email !== '') {
            step2.find("div.hints.email-found").show().find("a.email").attr('href', 'mailto:' + result.email).text(result.email);
            step2.find("input[name='email']").val(result.email);
        } else {
            step2.find("div.hints.email-not-found").show();
        }

        step1.fadeOut(function() {
            // Wait for fadeOut to complete before fadeIn
            step2.fadeIn();
        });
    }

    $("a.trigger-memberid-hint").click(function() {
        $("div.memberid-hint-modal").modal();
    });

});
