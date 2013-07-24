$(document).ready(function() {

    var form = $("form.register-membership");
    var country_select = form.find("select[name='country']");
    var zipcode_control_group = form.find("div.control-group.zipcode");

    Validator.validate({
        method: 'memberid',
        control_group: form.find("div.control-group.memberid"),
        input: form.find("input[name='memberid']"),
        req: true
    });

    Validator.validateZipcode(
        form.find("div.control-group.zipcode"),
        form.find("input[name='zipcode']"),
        form.find("input[name='area']"),
        form.find("img.ajaxloader.zipcode")
    );

    Validator.validate({
        method: 'email',
        control_group: form.find("div.control-group.email"),
        input: form.find("input[name='email']"),
        req: true
    });

    country_select.change(function() {
        if($(this).find("option:selected").val() == 'NO') {
            zipcode_control_group.show();
        } else {
            zipcode_control_group.hide();
        }
    });

    var memberid_accepted = false;
    var no_memberid_match = form.find("div.no-memberid-match");
    form.submit(function(e) {
        if(memberid_accepted) {
            return $(this);
        }
        no_memberid_match.hide();
        e.preventDefault();
        form.find("button[type='submit']").hide();
        form.find("img.ajaxloader.submit").show();
        $.ajaxQueue({
            url: form.attr('data-memberid-url'),
            data: {
                memberid: form.find("input[name='memberid']").val(),
                country: country_select.val(),
                zipcode: form.find("input[name='zipcode']").val()
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.exists) {
                if(!result.user_exists) {
                    memberid_accepted = true;
                    var email = form.find("div.control-group.email");
                    if(result.email == '' || result.email == email.attr('data-email')) {
                        form.find("input[name='email-equal']").val('true');
                        form.submit();
                    } else {
                        form.find("div.form-elements div.step1 input").prop('readonly', true);
                        form.find("div.form-elements div.step2").slideDown();
                        email.find("span.preselected-email.sherpa").text(email.attr('data-email'));
                        email.find("span.preselected-email.focus").text(result.email);
                    }
                } else {
                    form.find("div.user-exists").slideDown();
                }
                form.find("button[type='submit']").show();
            } else if(result.memberid_lookups_exceeded) {
                form.find("div.form-hints div.memberid-lookups-exceeded").slideDown();
            } else {
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

    form.find("input[name='email-choice']").change(function() {
        if(form.find("input[name='email-choice']:checked").val() == 'custom') {
            form.find("input[name='email']").prop('disabled', false);
        } else {
            form.find("input[name='email']").prop('disabled', true);
            form.find("div.control-group.email").removeClass('error success');
        }
    });

});
