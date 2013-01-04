$(document).ready(function() {

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

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

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
                if(!result.profile_exists) {
                    memberid_accepted = true;
                    var email = $("div.control-group.email");
                    if(result.email == '' || result.email == email.attr('data-email')) {
                        form.find("input[name='email-equal']").val('true');
                        form.submit();
                    } else {
                        $("div.form-elements div.step1 input").attr('readonly', true);
                        $("div.form-elements div.step2").slideDown();
                        email.find("span.preselected-email.sherpa").text(email.attr('data-email'));
                        email.find("span.preselected-email.focus").text(result.email);
                    }
                } else {
                    $("div.profile-exists").slideDown();
                }
                form.find("button[type='submit']").show();
            } else if(result.memberid_lookups_exceeded) {
                $("div.form-hints div.memberid-lookups-exceeded").slideDown();
            } else {
                no_memberid_match.find("span.memberid").text(form.find("input[name='memberid']").val());
                no_memberid_match.find("span.zipcode").text(form.find("input[name='zipcode']").val());
                no_memberid_match.slideDown();
                form.find("button[type='submit']").show();
            }
            form.find("img.ajaxloader.submit").hide();
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            form.find("button[type='submit']").show();
            form.find("img.ajaxloader.submit").hide();
        });
    });

    $("input[name='email-choice']").change(function() {
        if($("input[name='email-choice']:checked").val() == 'custom') {
            $("input[name='email']").removeAttr('disabled');
        } else {
            $("input[name='email']").attr('disabled', true);
            $("div.control-group.email").removeClass('error success');
        }
    });

});
