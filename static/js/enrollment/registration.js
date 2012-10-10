$(document).ready(function() {

    $("form#registration input[name='dob']").datepicker({
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
    $("form#registration input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning success');
    });

    var validator = new Validator();

    // Generic validation-complete function for most of the controls
    function markInput(el, valid) {
        if(valid) {
            el.parents("div.control-group").addClass('success');
        } else {
            el.parents("div.control-group").addClass('error');
        }
    }

    validator.addValidation('full_name', $("form#registration input[name='name']"), markInput, true);
    validator.addValidation('phone', $("form#registration input[name='phone']"), markInput, phone_required);
    validator.addValidation('email', $("form#registration input[name='email']"), markInput, email_required);

    window.validateDatepicker = validateDatepicker;
    function validateDatepicker() {
        // Datepicker calls this on close
        var dob = $("form#registration input[name='dob']");
        markInput(dob, validator.validate('date', dob.val(), true, {'min_year': 1900}));
    }

    $("a.step2").click(function(e) {
        // Check that conditions checkbox is checked
        if(!$("input.conditions").prop('checked')) {
            e.preventDefault();
            alert("Du kan ikke gå videre med mindre du har lest og godtatt betingelsene.");
            return;
        }
        if($(this).hasClass('post') || $("form#registration input[name='name']").val().length > 0) {
            e.preventDefault();
            $("form#registration").prepend('<input type="hidden" name="forward" value="1">').submit();
        }
    });

    /* Close conditions-dialog */
    $("div.dialog.conditions a.close-dialog").click(function() {
        $("div.dialog.conditions").dialog('close');
    });

});

function validateGender() {
    if($("form#registration input[name='gender']:checked").length == 0) {
        $("form#registration div.control-group.gender").addClass('error');
    } else {
        $("form#registration div.control-group.gender").addClass('success');
    }
}
