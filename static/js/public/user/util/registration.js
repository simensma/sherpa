$(function() {

    var memberid_accepted = false;
    var memberid_hint_modal = $("div.memberid-hint-modal");
    var registration = $("div.registration-form-wrapper");
    var registration_form = registration.find("form");
    var no_memberid_match = registration.find("div.no-memberid-match");
    var actor_is_not_member = registration.find("div.actor-is-not-member");
    var country_select = registration.find("select[name='country']");
    var zipcode_form_group = registration.find('[data-dnt-form-group="zipcode"]');

    Validator.validate({
        method: 'email',
        form_group: registration.find('[data-dnt-form-group="email"]'),
        input: registration.find("input[name='email']"),
        req: true
    });

    Validator.validatePasswords({
        form_group: registration.find('[data-dnt-form-group="password"], [data-dnt-form-group="password-repeat"]'),
        pass1: registration.find("input[name='password']"),
        pass2: registration.find("input[name='password-repeat']"),
        min_length: Turistforeningen.user_password_length,
        hints: registration.find('[data-dnt-form-group="password"] div.controls .help-block.validator')
    });

    Validator.validate({
        method: 'memberid',
        form_group: registration.find('[data-dnt-form-group="memberid"]'),
        input: registration.find("input[name='memberid']"),
        req: true
    });

    Validator.validateZipcode(
        registration.find('[data-dnt-form-group="zipcode"]'),
        registration.find("input[name='zipcode']"),
        registration.find("input[name='area']"),
        registration.find("img.ajaxloader.zipcode")
    );

    country_select.chosen();
    country_select.change(function() {
        if($(this).find("option:selected").val() == 'NO') {
            zipcode_form_group.show();
        } else {
            zipcode_form_group.hide();
        }
    });

    registration_form.submit(function(e) {
        if(memberid_accepted) {
            step2.find("button[type='submit']").prop('disabled', true);
            step2.find("img.ajaxloader.submit").show();
            return $(this);
        }
        no_memberid_match.hide();
        actor_is_not_member.hide();
        e.preventDefault();
        step1.find("button[type='submit']").hide();
        step1.find("img.ajaxloader.submit").show();
        $.ajaxQueue({
            url: registration_form.attr('data-memberid-url'),
            data: {
                memberid: registration.find("input[name='memberid']").val(),
                country: country_select.val(),
                zipcode: registration.find("input[name='zipcode']").val()
            }
        }).done(function(result) {
            result = JSON.parse(result);
            if(result.actor_is_not_member) {
                actor_is_not_member.slideDown();
                step1.find("button[type='submit']").show();
                registration.find("img.ajaxloader.submit").hide();
            } else if(result.exists) {
                if(!result.user_exists) {
                    enableStep2(result);
                } else {
                    registration.find("img.ajaxloader.submit").hide();
                    registration.find("div.user-exists").slideDown();
                }
            } else if(result.memberid_lookups_exceeded) {
                registration.find("img.ajaxloader.submit").hide();
                registration.find("div.memberid-lookups-exceeded").slideDown();
            } else {
                no_memberid_match.slideDown();
                step1.find("button[type='submit']").show();
                registration.find("img.ajaxloader.submit").hide();
            }
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved sjekk av medlemsnummeret. Vennligst prøv igjen senere.");
            step1.find("button[type='submit']").show();
            step1.find("img.ajaxloader.submit").hide();
        });
    });

    var step1 = registration.find("div.step1");
    var step2 = registration.find("div.step2");

    function enableStep2(result) {
        memberid_accepted = true;

        step2.find("span.name").text(result.name);
        if(result.email !== '') {
            step2.find(".help-block.email-found").show().find("a.email").attr('href', 'mailto:' + result.email).text(result.email);
            step2.find("input[name='email']").val(result.email);
        } else {
            step2.find(".help-block.email-not-found").show();
        }

        if(window.Turistforeningen.prefilled_user === undefined) {
            step1.fadeOut(function() {
                // Wait for fadeOut to complete before fadeIn
                step2.fadeIn();
            });
        } else {
            // We're automatically going to step2 - skip the fade-effects
            step1.hide();
            step2.show();
        }
    }

    registration.find("a.trigger-memberid-hint").click(function() {
        memberid_hint_modal.modal();
    });

    // Check if a pre-registrated user is filled out
    if(window.Turistforeningen.prefilled_user !== undefined) {
        registration_form.find("input[name='memberid']").val(window.Turistforeningen.prefilled_user.memberid);
        registration_form.find("input[name='zipcode']").val(window.Turistforeningen.prefilled_user.zipcode);
        registration_form.submit();
    }

});
