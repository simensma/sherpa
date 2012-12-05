window.datePickerCount = 1;

$(document).ready(function() {

    var giver_control_group = $("div.control-group.giver_zipcode");
    var giver_zipcode = $("input[name='giver_zipcode']");
    var giver_area = $("input[name='giver_area']");
    var giver_loader = giver_zipcode.siblings("img.ajaxloader");
    Validator.validateZipcode(giver_control_group, giver_zipcode, giver_area, giver_loader);
    if(giver_zipcode.val() != '') {
        Validator.triggerZipcode(giver_zipcode);
    }

    Validator.validate({
        method: 'full_name',
        control_group: $("form#gift div.control-group.giver_name"),
        input: $("form#gift input[name='giver_name']"),
        req: true
    });

    Validator.validate({
        method: 'address',
        control_group: $("form#gift div.control-group.giver_address"),
        input: $("form#gift input[name='giver_address']"),
        req: true
    });

    Validator.validate({
        method: 'memberid',
        control_group: $("form#gift div.control-group.giver_memberid"),
        input: $("form#gift input[name='giver_memberid']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        control_group: $("form#gift div.control-group.giver_phone"),
        input: $("form#gift input[name='giver_phone']"),
        req: false
    });

    Validator.validate({
        method: 'email',
        control_group: $("form#gift div.control-group.giver_email"),
        input: $("form#gift input[name='giver_email']"),
        req: false
    });


    function addReceiverValidations(box) {
        Validator.validate({
            method: 'full_name',
            control_group: box.find("div.control-group.receiver_name"),
            input: box.find("input[name='receiver_name']"),
            req: true
        });

        Validator.validate({
            method: 'address',
            control_group: box.find("div.control-group.receiver_address"),
            input: box.find("input[name='receiver_address']"),
            req: true
        });

        Validator.validate({
            method: 'phone',
            control_group: box.find("div.control-group.receiver_phone"),
            input: box.find("input[name='receiver_phone']"),
            req: false
        });

        Validator.validate({
            method: 'email',
            control_group: box.find("div.control-group.receiver_email"),
            input: box.find("input[name='receiver_email']"),
            req: false
        });

        Validator.validateZipcode(
            box.find("div.control-group.receiver_zipcode"),
            box.find("input[name='receiver_zipcode']"),
            box.find("input[name='receiver_area']"),
            box.find("div.control-group.receiver_zipcode img.ajaxloader")
        );

        var dob = box.find("input[name='receiver_dob']");
        dob.datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            startView: 'decade',
            autoclose: true,
            language: 'nb'
        }).on('hide', function() {
            Validator.performValidation({
                method: 'date',
                control_group: box.find("div.control-group.receiver_dob"),
                input: dob,
                req: true
            });
        });
    }

    function addReceiver() {
        var clone = $("div.receiver-box-skeleton").clone();
        clone.removeClass('receiver-box-skeleton').addClass('receiver-box');
        $("form#gift div.receivers").append(clone);
        var new_receiver = $("p.new-receiver");
        new_receiver.detach();
        $("div.receiver-box").last().append(new_receiver);
        clone.find("div.control-group.receiver_type").popover();
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
                dob: $(this).find("input[name='receiver_dob']").val(),
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
            div.find("input[name='receiver_dob']").val(session_receivers[i].dob);
            div.find("input[name='receiver_address']").val(session_receivers[i].address);
            div.find("input[name='receiver_zipcode']").val(session_receivers[i].zipcode);
            div.find("input[name='receiver_area']").val(session_receivers[i].area);
            div.find("input[name='receiver_phone']").val(session_receivers[i].phone);
            div.find("input[name='receiver_email']").val(session_receivers[i].email);
        }
    }

    if(window.trigger_form_validations) {
        Validator.trigger();
        $("div.receiver-box input[name='receiver_dob']").datepicker('hide');
        Validator.triggerZipcode($("input[name='receiver_zipcode']"));
    }
});
