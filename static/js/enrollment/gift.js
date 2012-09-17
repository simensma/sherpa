window.datePickerCount = 1;

$(document).ready(function() {
    $("select.skel[name='receiver_type']").clone().show().appendTo($("form#gift div.receiver_type")).chosen({disable_search: true});

    $(document).on('keyup', 'form#gift input.zipcode', function() {
        var self = $(this);
        if(self.val().match(/^\d{4}$/)) {
            self.siblings("img.ajaxloader").show();
            $.ajaxQueue({
                url: '/postnummer/' + encodeURIComponent(self.val()) + '/',
                type: 'POST'
            }).done(function(result) {
                result = JSON.parse(result);
                if(result.location != undefined) {
                    self.siblings("input.city").val(result.location);
                    self.parents("div.control-group").removeClass('error').addClass('success');
                } else if(result.error == "does_not_exist") {
                    self.siblings("input.city").val("Ukjent postnummer");
                    self.parents("div.control-group").removeClass('success').addClass('error');
                }
            }).fail(function(result) {
                self.siblings("input.city").val("Teknisk feil");
                self.parents("div.control-group.zipcode").removeClass('success').addClass('error');
            }).always(function(result) {
                self.siblings("img.ajaxloader").hide();
            });
        } else {
            self.siblings("input.city").val("");
            self.parents("div.control-group").removeClass('error warning success');
        }
    });

    // Clear input validation-status upon focus
    $(document).on('focus', "form#gift input", function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    var validator = new Validator();

    // Generic validation-complete function for most of the controls
    function markInput(el, valid) {
        if(valid) {
            el.parents("div.control-group").addClass('success');
        } else {
            el.parents("div.control-group").addClass('error');
        }
    }

    function markInputZipcode(el, valid) {
        if(!valid) {
            el.parents("div.control-group").addClass('error');
        }
        // Ignore if valid, let ajax mark it based on zipcode lookup
    }

    validator.addValidation('full_name', $("form#gift input[name='giver_name']"), markInput, true);
    validator.addValidation('address', $("form#gift input[name='giver_address']"), markInput, true);
    validator.addValidation('zipcode', $("form#gift input[name='giver_zipcode']"), markInputZipcode, true);
    validator.addValidation('memberno', $("form#gift input[name='giver_memberno']"), markInput, false);
    validator.addValidation('phone', $("form#gift input[name='giver_phone']"), markInput, false);
    validator.addValidation('email', $("form#gift input[name='giver_email']"), markInput, false);

    addReceiverValidations($("form#gift div.receiver-box"));

    function addReceiverValidations(box) {
        validator.addValidation('full_name', box.find("input[name='receiver_name']"), markInput, true);
        validator.addValidation('address', box.find("input[name='receiver_address']"), markInput, true);
        validator.addValidation('zipcode', box.find("input[name='receiver_zipcode']"), markInputZipcode, true);
        validator.addValidation('phone', box.find("input[name='receiver_phone']"), markInput, false);
        validator.addValidation('email', box.find("input[name='receiver_email']"), markInput, false);

        var forms = {};
        forms[box.find("select.dob.dd").attr('id')]= "%d";
        forms[box.find("select.dob.mm").attr('id')]= "%n";
        forms[box.find("select.dob.yyyy").attr('id')]= "%Y";
        datePickerController.createDatePicker({
            formElements: forms,
            statusFormat:"%d. %F %Y",
            noTodayButton:true,
            positioned: box.find("span.dob-placement").attr('id')
        });
    }

    function validateDatepicker() {
        // Datepicker calls this on close
        markInput($(this), validator.validate('date', $("form#gift input[name='receiver_dob']").val(), true));
    }

    // Add more receivers
    $("form#gift button.new-receiver").click(function(e) {
        e.preventDefault();
        var list = $("form#gift div.receiver-box");
        var clone = list.first().clone();
        clone.addClass('hide');
        list.last().after(clone);
        var type = clone.find("div.receiver_type").empty();
        var select = $("select.skel[name='receiver_type']").clone().removeClass('skel').show().appendTo(type);
        var button = $('<button class="btn btn-danger remove-receiver"><i class="icon-remove"></i> Ta bort denne mottakeren</button>');
        button.click(function(e) {
            e.preventDefault();
            $(this).parents('div.receiver-box').slideUp(function() { $(this).remove(); });
        });
        clone.append(button);
        clone.find("div.control-group").removeClass('error warning success').focus(function() {
            $(this).parents("div.control-group").removeClass('error warning success');
        });
        clone.find("input").val("");
        window.datePickerCount += 1;
        var dd = clone.find("select.dob.dd");
        var mm = clone.find("select.dob.mm");
        var yyyy = clone.find("select.dob.yyyy");
        var placement = clone.find("span.dob-placement");
        placement.empty();
        dd.removeAttr('id').attr('id', 'dp-dd-' + window.datePickerCount);
        mm.removeAttr('id').attr('id', 'dp-mm-' + window.datePickerCount);
        yyyy.removeAttr('id').attr('id', 'dp-yyyy-' + window.datePickerCount);
        placement.removeAttr('id').attr('id', 'dob-placement-' + window.datePickerCount);
        dd.siblings("a").remove();
        addReceiverValidations(clone);
        select.chosen({disable_search: true});
        clone.slideDown();
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
                zipcode: $(this).find("input[name='receiver_zipcode']").val()
            };
            receivers.push(receiver);
        });
        $("form#gift input[name='receivers']").val(JSON.stringify(receivers));
    });

});
