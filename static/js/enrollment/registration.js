$(document).ready(function() {

    var form = $("form#registration");

    form.find("input[name='dob']").datepicker({
        changeMonth: true,
        changeYear: true,
        firstDay: 1,
        yearRange: "1900:c", // Based on earliest possible mssql smalldatetime value
        dateFormat: 'dd.mm.yy',
        dayNames: ['Søndag', 'Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag'],
        dayNamesShort: ['Søn', 'Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør'],
        dayNamesMin: ['Sø', 'Ma', 'Ti', 'On', 'To', 'Fr', 'Lø'],
        monthNames: ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August',
          'September', 'Oktober', 'November', 'Desember'],
        monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt',
          'Nov', 'Des'],
        defaultDate: '-15y',
        showOn: 'both',
        buttonImage: '/static/img/calendar.png',
        buttonImageOnly: true,
        buttonText: 'Velg dato...',
        onClose: validateDatepicker
    });

    // Clear input validation-status upon focus
    form.find("input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    Validator.validate({
        method: 'full_name',
        control_group: form.find("div.control-group.name"),
        input: form.find("input[name='name']"),
        req: true
    });

    Validator.validate({
        method: 'phone',
        control_group: form.find("div.control-group.phone"),
        input: form.find("input[name='phone']"),
        req: Turistforeningen.phone_required
    });

    Validator.validate({
        method: 'email',
        control_group: form.find("div.control-group.email"),
        input: form.find("input[name='email']"),
        req: Turistforeningen.email_required
    });


    window.validateDatepicker = validateDatepicker;
    function validateDatepicker() {
        // Datepicker calls this on close
        Validator.performValidation({
            method: 'date',
            control_group: form.find("div.control-group.dob"),
            input: form.find("input[name='dob']"),
            req: true,
            opts: {'min_year': 1900}
        });
    }

    function validateGender() {
        if(form.find("input[name='gender']:checked").length == 0) {
            form.find("div.control-group.gender").addClass('error');
        } else {
            form.find("div.control-group.gender").addClass('success');
        }
    }

    $("a.step2").click(function(e) {
        // Check that conditions checkbox is checked
        if(!$("input.conditions").prop('checked')) {
            e.preventDefault();
            alert("Du kan ikke gå videre med mindre du har lest og godtatt betingelsene.");
            return;
        }
        if($(this).hasClass('post') || form.find("input[name='name']").val().length > 0) {
            e.preventDefault();
            form.prepend('<input type="hidden" name="forward" value="1">').submit();
        }
    });

    /* Close conditions-dialog */
    $("div.dialog.conditions a.close-dialog").click(function() {
        $("div.dialog.conditions").dialog('close');
    });

    form.submit(function() {
        // The adform guys advised us to defer this call even though it probably shouldn't be
        setTimeout(function() {
            if(typeof adf !== 'undefined') {
                adf.track(133425,2765715,{});
            }
        }, 0);
    });

    if(window.trigger_form_validations) {
        Validator.trigger();
        validateDatepicker();
        validateGender();
    }

});
