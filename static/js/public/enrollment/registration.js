$(function() {

    var registration = $("div.enrollment-registration");
    var form = registration.find('[data-dnt-container="registration-form"]');

    var continue_button = form.find('[data-dnt-button="continue"]');

    // startDate is based on the earliest possible mssql smalldatetime value
    var now = new Date();
    var startDate = new Date(1900, 0, 1, 0, 0, 0, 0);
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
    form.find("div.date").datepicker({
        format: 'dd.mm.yyyy',
        startDate: startDate,
        endDate: today,
        startView: 'decade',
        weekStart: 1,
        autoclose: true,
        forceParse: false
    }).on('hide', validateDatepicker);

    // Clear input validation-status upon focus
    form.find("input").focus(function() {
        $(this).parents('[data-dnt-form-group]').removeClass('has-error has-warning has-success');
    });

    Validator.validate({
        method: 'full_name',
        form_group: form.find('[data-dnt-form-group="name"]'),
        input: form.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'phone',
        form_group: form.find('[data-dnt-form-group="phone"]'),
        input: form.find("input[name='phone']"),
        req: Turistforeningen.phone_required
    });

    Validator.validate({
        method: 'email',
        form_group: form.find('[data-dnt-form-group="email"]'),
        input: form.find("input[name='email']"),
        req: Turistforeningen.email_required
    });


    window.validateDatepicker = validateDatepicker;
    function validateDatepicker() {
        // Datepicker calls this on close
        Validator.performValidation({
            method: 'date',
            form_group: form.find('[data-dnt-form-group="dob"]'),
            input: form.find("input[name='dob']"),
            req: true,
            opts: {'min_year': 1900, 'max_year': 2078}
        });

        // The datepicker will return an invalid date if it's in the future
        var date = form.find('.date').datepicker('getDate');
        if(date.toString() === "Invalid Date") {
            form.find('[data-dnt-form-group="dob"]').removeClass('has-success').addClass('has-error');
        }
    }

    function validateGender() {
        if(form.find("input[name='gender']:checked").length === 0) {
            form.find('[data-dnt-form-group="gender"]').addClass('has-error');
        } else {
            form.find('[data-dnt-form-group="gender"]').addClass('has-success');
        }
    }

    form.submit(function(e) {
        // Check that conditions checkbox is checked
        var is_continuing = form.find('input[name="button"]').val() === 'continue';
        if(is_continuing && !registration.find("input.conditions").prop('checked')) {
            e.preventDefault();
            alert(continue_button.attr("data-conditions-message"));
            return;
        }
    });

    // Post which button the user clicked on
    continue_button.click(function() {
        form.find('input[name="button"]').val($(this).attr('data-dnt-button'));
        form.submit();
    });

    if(Turistforeningen.trigger_form_validations) {
        Validator.trigger();
        validateDatepicker();
        validateGender();
    }

});
