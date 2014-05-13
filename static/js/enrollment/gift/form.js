$(function() {

    var giver_control_group = $("div.control-group.giver_zipcode");
    var giver_zipcode = $("input[name='giver_zipcode']");
    var giver_area = $("input[name='giver_area']");
    var giver_loader = giver_zipcode.siblings("img.ajaxloader");
    Validator.validateZipcode(giver_control_group, giver_zipcode, giver_area, giver_loader);
    if(giver_zipcode.val() !== '') {
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


    function addReceiverValidations(box, initial_date) {
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

        var dob = box.find("div.control-group.receiver_dob div.date");
        dob.find("input[name='receiver_dob']").val(initial_date);
        dob.datepicker({
            format: 'dd.mm.yyyy',
            weekStart: 1,
            startView: 'decade',
            autoclose: true,
            forceParse: false
        }).on('changeDate', function() {
            Validator.performValidation({
                method: 'date',
                control_group: box.find("div.control-group.receiver_dob"),
                input: dob.find("input[name='receiver_dob']"),
                req: true
            });
        });
    }

    function addReceiver(initial_date) {
        var clone = $("div.receiver-box-skeleton").clone();
        clone.removeClass('receiver-box-skeleton').addClass('receiver-box');
        $("form#gift div.receivers").append(clone);
        var new_receiver = $("p.new-receiver");
        new_receiver.detach();
        $("div.receiver-box").last().append(new_receiver);
        clone.find("div.control-group.receiver_type").popover();
        clone.find("select[name='receiver_type']").chosen({disable_search: true});
        addReceiverValidations(clone, initial_date);
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

    if(Turistforeningen.session_receivers.length === 0) {
        addReceiver();
    } else {
        for(var i=0; i<Turistforeningen.session_receivers.length; i++) {
            var div = addReceiver(Turistforeningen.session_receivers[i].dob);

            // Pre-insert form data
            div.find("select[name='receiver_type'] option[value='"+ Turistforeningen.session_receivers[i].type_index + "']").prop('selected', true);
            div.find("select[name='receiver_type']").trigger("liszt:updated"); // Update chosen
            div.find("input[name='receiver_name']").val(Turistforeningen.session_receivers[i].name);
            div.find("input[name='receiver_address']").val(Turistforeningen.session_receivers[i].address);
            div.find("input[name='receiver_zipcode']").val(Turistforeningen.session_receivers[i].zipcode);
            div.find("input[name='receiver_area']").val(Turistforeningen.session_receivers[i].area);
            div.find("input[name='receiver_phone']").val(Turistforeningen.session_receivers[i].phone);
            div.find("input[name='receiver_email']").val(Turistforeningen.session_receivers[i].email);
        }
    }

    if(window.trigger_form_validations) {
        Validator.trigger();
        $("div.receiver-box div.control-group.receiver_dob div.date").datepicker('hide');
        Validator.triggerZipcode($("input[name='giver_zipcode'], input[name='receiver_zipcode']"));
    }
});
