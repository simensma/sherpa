$(document).ready(function() {

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.email"),
        input: $("input[name='email']"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.title"),
        input: $("input[name='title']"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.text"),
        input: $("textarea[name='text']"),
        req: true
    });

});
