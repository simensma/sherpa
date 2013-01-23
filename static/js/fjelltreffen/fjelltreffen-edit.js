$(document).ready(function() {

    Validator.validate({
        method: 'email',
        control_group: $("div.control-group.annonse-email-control"),
        input: $("input.annonse-email"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.annonse-title-control"),
        input: $("input.annonse-title"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: $("div.control-group.annonse-text-control"),
        input: $("textarea.annonse-text"),
        req: true
    });

});
