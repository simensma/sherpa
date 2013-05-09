$(document).ready(function() {

    var memberid_accepted = false;
    var no_memberid_match = $("div.no-memberid-match");
    var registration_form = $("div.registration-form-wrapper form");
    var country_select = registration_form.find("select[name='country']");
    var zipcode_control_group = registration_form.find("div.control-group.zipcode");

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

    country_select.chosen();
    country_select.change(function() {
        if($(this).find("option:selected").val() == 'NO') {
            zipcode_control_group.show();
        } else {
            zipcode_control_group.hide();
        }
    });

    registration_form.submit(function(e) {
        if(memberid_accepted) {
            step2.find("button[type='submit']").prop('disabled', true);
            step2.find("img.ajaxloader.submit").show();
            return $(this);
        }
        no_memberid_match.hide();
        e.preventDefault();
        step1.find("button[type='submit']").hide();
        step1.find("img.ajaxloader.submit").show();
        $.ajaxQueue({
            url: '/minside/sjekk-medlemsnummer/',
            data: {
                memberid: registration_form.find("input[name='memberid']").val(),
                country: country_select.val(),
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
                no_memberid_match.slideDown();
                step1.find("button[type='submit']").show();
                registration_form.find("img.ajaxloader.submit").hide();
            }
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            step1.find("button[type='submit']").show();
            step1.find("img.ajaxloader.submit").hide();
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
