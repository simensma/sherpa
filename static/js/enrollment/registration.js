$(document).ready(function() {

    $("form#registration input[name='dob']").datepicker({
        changeMonth: true,
        changeYear: true,
        firstDay: 1,
        yearRange: "-120:c",
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

    $("form#registration input").focus(function() {
        $(this).parents("div.control-group").removeClass('error warning');
    });

    $("form#registration input[name='name']").focusout(function() {
        if(!$(this).val().match(/.+\s.+/)) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    window.phone_required = false;
    $("form#registration input[name='phone']").focusout(function() {
        if($(this).val() != "" && ($(this).val().length < 8 || $(this).val().match(/[a-z]/i))) {
            $(this).parents("div.control-group").addClass('error');
        }
        if(phone_required && $(this).val() == '') {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    window.email_required = false;
    $("form#registration input[name='email']").focusout(function() {
        if($(this).val() != "" && !$(this).val().match(/^\s*[^\s]+@[^\s]+\.[^\s]+\s*$/)) {
            // Email provided, but invalid
            $(this).parents("div.control-group").addClass('error');
        }
        if(email_required && $(this).val() == "") {
            $(this).parents("div.control-group").addClass('error');
        }
    });

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

function validateDatepicker() {
    if(!$("form#registration input[name='dob']").val().match(/\d\d\.\d\d\.\d\d\d\d/)) {
        $("form#registration div.control-group.dob").addClass('error');
    }
}

function validateGender() {
    if($("form#registration input[name='gender']:checked").length == 0) {
        $("form#registration div.control-group.gender").addClass('error');
    }
}
