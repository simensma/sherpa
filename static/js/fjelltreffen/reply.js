$(document).ready(function() {

    var form = $("form.fjelltreffen-annonse-reply");

    Validator.validate({
        method: 'full_name',
        control_group: form.find("div.control-group.name"),
        input: form.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        control_group: form.find("div.control-group.email"),
        input: form.find("input[name='email']"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        control_group: form.find("div.control-group.text"),
        input: form.find("textarea[name='text']"),
        req: true
    });

    // Response

    var response_wrapper = $("div.fjelltreffen-response");

    response_wrapper.find("ul.response a[data-response]").click(function() {
        var response = $(this).attr("data-response");
        $(this).parents("ul").remove();
        response_wrapper.find("div." + response).slideDown();
    });

});