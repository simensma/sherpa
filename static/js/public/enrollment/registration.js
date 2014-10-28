$(function() {

    var registration = $("div.enrollment-registration");
    var form = registration.find('[data-dnt-container="registration-form"]');

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
        if(form.find("input[name='gender']:checked").length == 0) {
            form.find('[data-dnt-form-group="gender"]').addClass('has-error');
        } else {
            form.find('[data-dnt-form-group="gender"]').addClass('has-success');
        }
    }

    registration.find("a.step2").click(function(e) {
        // Check that conditions checkbox is checked
        if(!registration.find("input.conditions").prop('checked')) {
            e.preventDefault();
            alert($(this).attr("data-conditions-message"));
            return;
        }
        if($(this).hasClass('post') || form.find("input[name='name']").val().length > 0) {
            e.preventDefault();
            form.prepend('<input type="hidden" name="forward" value="1">').submit();
        }
    });

    if(Turistforeningen.trigger_form_validations) {
        Validator.trigger();
        validateDatepicker();
        validateGender();
    }

});
