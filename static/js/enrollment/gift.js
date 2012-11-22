window.datePickerCount = 1;

$(document).ready(function() {

    $(document).on('keyup focusout', 'form#gift input.zipcode', function() {
        var self = $(this);
        if(self.val().match(/^\d{4}$/)) {
            self.siblings("img.ajaxloader").show();
            $.ajaxQueue({
                url: '/postnummer/' + encodeURIComponent(self.val()) + '/'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.area != undefined) {
                    self.siblings("input.area").val(result.area);
                    self.parents("div.control-group").removeClass('error').addClass('success');
                } else if(result.error == "does_not_exist") {
                    self.siblings("input.area").val("Ukjent postnummer");
                    self.parents("div.control-group").removeClass('success').addClass('error');
                }
            }).fail(function(result) {
                self.siblings("input.area").val("Teknisk feil");
                self.parents("div.control-group").removeClass('success').addClass('error');
            }).always(function(result) {
                self.siblings("img.ajaxloader").hide();
            });
        } else {
            self.parents("div.control-group").removeClass('error success');
            self.siblings("input.area").val("");
            if(!$(this).is(":focus")) {
                self.parents("div.control-group").addClass('error');
            }
        }
    });

    // Clear input validation-status upon focus
    $(document).on('focus', "form#gift input", function() {
        $(this).parents("div.control-group").removeClass('error success');
    });

    window.validator = new Validator();

    // Generic validation-complete function for most of the controls
    function markInput(el, valid) {
        if(valid) {
            el.parents("div.control-group").addClass('success');
        } else {
            el.parents("div.control-group").addClass('error');
        }
    }

    validator.addValidation('full_name', $("form#gift input[name='giver_name']"), markInput, true);
    validator.addValidation('address', $("form#gift input[name='giver_address']"), markInput, true);
    validator.addValidation('memberno', $("form#gift input[name='giver_memberno']"), markInput, false);
    validator.addValidation('phone', $("form#gift input[name='giver_phone']"), markInput, false);
    validator.addValidation('email', $("form#gift input[name='giver_email']"), markInput, false);

    function addReceiverValidations(box) {
        validator.addValidation('full_name', box.find("input[name='receiver_name']"), markInput, true);
        validator.addValidation('address', box.find("input[name='receiver_address']"), markInput, true);
        validator.addValidation('phone', box.find("input[name='receiver_phone']"), markInput, false);
        validator.addValidation('email', box.find("input[name='receiver_email']"), markInput, false);

        var forms = {};
        forms[box.find("select[name='receiver_dob_dd']").attr('id')]= "%d";
        forms[box.find("select[name='receiver_dob_mm']").attr('id')]= "%n";
        forms[box.find("select[name='receiver_dob_yyyy']").attr('id')]= "%Y";
        datePickerController.createDatePicker({
            formElements: forms,
            statusFormat:"%d. %F %Y",
            noTodayButton:true,
            positioned: box.find("span.dob-placement").attr('id')
        });
    }

    function addReceiver() {
        var clone = $("div.receiver-box-skeleton").clone();
        clone.removeClass('receiver-box-skeleton').addClass('receiver-box');
        $("form#gift div.receivers").append(clone);
        var new_receiver = $("p.new-receiver");
        new_receiver.detach();
        $("div.receiver-box").last().append(new_receiver);
        clone.find("select[name='receiver_type']").chosen({disable_search: true})
        window.datePickerCount += 1;
        clone.find("select[name='receiver_dob_dd']").attr('id', 'dp-dd-' + window.datePickerCount);
        clone.find("select[name='receiver_dob_mm']").attr('id', 'dp-mm-' + window.datePickerCount);
        clone.find("select[name='receiver_dob_yyyy']").attr('id', 'dp-yyyy-' + window.datePickerCount);
        clone.find("span.dob-placement").attr('id', 'dob-placement-' + window.datePickerCount);
        addReceiverValidations(clone);
        clone.slideDown();
        return clone;
    }

    // Add more receivers
    $("form#gift button.new-receiver").click(function(e) {
        e.preventDefault();
        addReceiver();
    });

    // Remove a receiver
    $(document).on('click', 'form#gift button.remove-receiver', function(e) {
        e.preventDefault();
        $(this).parents('div.receiver-box').slideUp(function() {
            var new_receiver = $("p.new-receiver");
            new_receiver.detach();
            $(this).remove();
            $("div.receiver-box").last().append(new_receiver);
        });
    });


    $("form#gift button[type='submit']").click(function(e) {
        var receivers = [];
        $("form#gift div.receiver-box").each(function() {
            var receiver = {
                type: $(this).find("select[name='receiver_type'] option:selected").val(),
                name: $(this).find("input[name='receiver_name']").val(),
                dob: $(this).find("select[name='receiver_dob_dd'] option:selected").val() + "." +
                     $(this).find("select[name='receiver_dob_mm'] option:selected").val() + "." +
                    $(this).find("select[name='receiver_dob_yyyy'] option:selected").val(),
                address: $(this).find("input[name='receiver_address']").val(),
                zipcode: $(this).find("input[name='receiver_zipcode']").val(),
                phone: $(this).find("input[name='receiver_phone']").val(),
                email: $(this).find("input[name='receiver_email']").val()
            };
            receivers.push(receiver);
        });
        $("form#gift input[name='receivers']").val(JSON.stringify(receivers));
    });

    if(session_receivers.length == 0) {
        addReceiver();
    } else {
        for(var i=0; i<session_receivers.length; i++) {
            var div = addReceiver();

            // Pre-insert form data
            div.find("select[name='receiver_type'] option[value='"+ session_receivers[i].type_index + "']").attr('selected', true);
            div.find("select[name='receiver_type']").trigger("liszt:updated"); // Update chosen
            div.find("input[name='receiver_name']").val(session_receivers[i].name);
            div.find("select[name='receiver_dob_dd'] option[value='" + Number(session_receivers[i].dob_dd) + "']").attr('selected', true);
            div.find("select[name='receiver_dob_dd']").trigger("liszt:updated"); // Update chosen
            div.find("select[name='receiver_dob_mm'] option[value='" + Number(session_receivers[i].dob_mm) + "']").attr('selected', true);
            div.find("select[name='receiver_dob_mm']").trigger("liszt:updated"); // Update chosen
            div.find("select[name='receiver_dob_yyyy'] option[value='" + Number(session_receivers[i].dob_yyyy) + "']").attr('selected', true);
            div.find("select[name='receiver_dob_yyyy']").trigger("liszt:updated"); // Update chosen
            div.find("input[name='receiver_address']").val(session_receivers[i].address);
            div.find("input[name='receiver_zipcode']").val(session_receivers[i].zipcode);
            div.find("input[name='receiver_area']").val(session_receivers[i].area);
            div.find("input[name='receiver_phone']").val(session_receivers[i].phone);
            div.find("input[name='receiver_email']").val(session_receivers[i].email);
        }
    }

    $(document).trigger('validator_ready');
});
