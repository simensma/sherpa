$(document).ready(function() {

    Validator.validate({
        method: 'full_name',
        control_group: $("div.control-group.name"),
        input: $("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

    var control_group = $("div.control-group.sherpa-email");
    if(control_group.length > 0) {
        Validator.validate({
            method: 'email',
            control_group: control_group,
            input: control_group.find("input[name='sherpa-email']"),
            req: false
        });
    }

    Validator.validate({
        method: 'phone',
        control_group: $("div.control-group.phone_home"),
        input: $("input[name='phone_home']"),
        req: false
    });

    Validator.validate({
        method: 'phone',
        control_group: $("div.control-group.phone_mobile"),
        input: $("input[name='phone_mobile']"),
        req: false
    });

    Validator.validate({
        method: 'address',
        control_group: $("div.control-group.address"),
        input: $("input[name='address']"),
        req: true
    });

    Validator.validateZipcode(
        $("div.control-group.zipcode"),
        $("input[name='zipcode']"),
        $("input[name='area']"),
        $("img.ajaxloader.zipcode")
    );

    // Trigger all validations
    Validator.trigger();
    Validator.triggerZipcode($("input[name='zipcode']"));

    $("input[name='toggle-sherpa-email']").change(function() {
        if($(this).is(':checked')) {
            $("input[name='sherpa-email']").removeAttr('readonly');
        } else {
            $("input[name='sherpa-email']").val('').attr('readonly', true).focusout();
        }
    });

});
