$(function() {

    var form = $("form.fjelltreffen-annonse-reply");

    Validator.validate({
        method: 'full_name',
        form_group: form.find("div.form-group.name"),
        input: form.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'email',
        form_group: form.find("div.form-group.email"),
        input: form.find("input[name='email']"),
        req: true
    });

    Validator.validate({
        method: 'anything',
        form_group: form.find("div.form-group.text"),
        input: form.find("textarea[name='text']"),
        req: true
    });

    // Response

    var response_wrapper = $("div.fjelltreffen-response");
    var reply = response_wrapper.find("div.reply");
    var report = response_wrapper.find("div.report");

    response_wrapper.find("button.reply").click(function() {
        $(this).parent().hide();
        reply.slideDown();
    });

    response_wrapper.find("a.report").click(function() {
        $(this).parent().hide();
        report.slideDown();
    });

});
