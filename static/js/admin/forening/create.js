$(function() {
    var admin = $("div.foreningsadmin");
    var form = admin.find("form.create-forening");
    var contact_person_search_modal = admin.find("div.contact-person-search");

    var type_input = form.find("select[name='create-type']");
    var group_type = form.find("div.group_type");
    var parent = form.find("div.parent");

    var zipcode = form.find("input[name='create-zipcode']");
    var area = form.find("input[name='create-area']");
    var loader = form.find("img.ajaxloader.zipcode");

    var choose_contact = form.find("div.choose-contact");
    var contact_person_name = form.find("div.contact_person_name");
    var contact_person_name_input = contact_person_name.find("input[name='create-contact_person_name']");
    var contact_person_input = contact_person_name.find("input[name='create-contact_person']");
    var contact_person_search = contact_person_name.find("a.search");
    var contact_person_manual = contact_person_name.find("a.manual");
    var contact_person_phone_input = form.find("input[name='create-phone']");
    var contact_person_email_input = form.find("input[name='create-email']");

    type_input.change(function() {
        if($(this).val() == 'sentral' || $(this).val() == 'forening') {
            parent.hide();
        } else {
            parent.show();
        }

        if($(this).val() == 'turgruppe') {
            group_type.show();
        } else {
            group_type.hide();
        }
    });
    // Trigger type-dependent logic - covers the case where the form was posted, but invalid,
    // and the input values are retained - since the template show/hide logic can't account for that
    type_input.change();

    zipcode.keyup(function() {
        if($(this).val().length === 4) {
            loader.show();
            LookupZipcode($(this).val(), function(result) {
                if(result.success) {
                    area.val(result.area);
                } else if(result.error == 'does_not_exist') {
                    area.val('Ukjent postnummer');
                } else if(result.error == 'technical_failure') {
                    area.val('Teknisk feil');
                }
                loader.hide();
            });
        } else {
            area.val('');
        }
    });

    choose_contact.find("input[type='radio']").change(function() {
        var val = choose_contact.find("input[type='radio']:checked").val();
        if(val === 'person') {
            contact_person_name.show();
        } else if(val === 'forening') {
            contact_person_name.hide();
            contact_person_input.val('');
            resetContactDetailsState();
        }
    });

    // Searching for a contact person in the member register
    contact_person_search.click(function() {
        AdminForeningContactPersonSearch.enable({
            callback: function(opts) {
                contact_person_input.val(opts.result_row.attr('data-id'));
                resetContactDetailsState();
                contact_person_name_input.val(opts.result_row.attr('data-name'));
                contact_person_phone_input.val(opts.result_row.attr('data-phone'));
                contact_person_email_input.val(opts.result_row.attr('data-email'));
                contact_person_search_modal.modal('hide');
            }
        });
    });

    // Fill contact person details manually
    contact_person_manual.click(function() {
        contact_person_input.val('');
        resetContactDetailsState();
        contact_person_name_input.prop('readonly', false);
        contact_person_phone_input.prop('readonly', false);
        contact_person_email_input.prop('readonly', false);
    });

    // Reset the contact info fields based on chosen-user state
    function resetContactDetailsState() {
        var chosen_contact = (contact_person_input.val() !== '');
        contact_person_name_input.prop('readonly', chosen_contact);
        contact_person_phone_input.prop('readonly', chosen_contact);
        contact_person_email_input.prop('readonly', chosen_contact);
        if(chosen_contact) {
            contact_person_search.hide();
            contact_person_manual.show();
        } else {
            contact_person_search.show();
            contact_person_manual.hide();
        }
    }

    // Reset the disabled state on page load - this is kind of hard to do through the Django forms API
    resetContactDetailsState();

});
