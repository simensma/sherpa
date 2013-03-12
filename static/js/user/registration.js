$(document).ready(function() {

    var memberid_accepted = false;
    var no_memberid_match = $("div.form-hints div.no-memberid-match");
    var form = $("form");

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
        hints: form.find("div.control-group.password div.controls div.hints.validator")
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

    form.submit(function(e) {
        if(memberid_accepted) {
            return $(this);
        }
        no_memberid_match.hide();
        e.preventDefault();
        var form = $(this);
        step1.find("button[type='submit']").hide();
        form.find("img.ajaxloader.submit").show();
        $.ajax({
            url: '/minside/sjekk-medlemsnummer/',
            data: {
                memberid: form.find("input[name='memberid']").val(),
                zipcode: form.find("input[name='zipcode']").val()
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
                form.find("img.ajaxloader.submit").hide();
                $("div.form-hints div.memberid-lookups-exceeded").slideDown();
            } else {
                no_memberid_match.find("span.memberid").text(form.find("input[name='memberid']").val());
                no_memberid_match.find("span.zipcode").text(form.find("input[name='zipcode']").val());
                no_memberid_match.slideDown();
                step1.find("button[type='submit']").show();
                form.find("img.ajaxloader.submit").hide();
            }
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            step1.find("button[type='submit']").show();
            form.find("img.ajaxloader.submit").hide();
        });
    });

    var step1 = form.find("div.step1");
    var step2 = form.find("div.step2");

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
