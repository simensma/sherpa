$(document).ready(function() {

    $("form#registration img.ajaxloader").hide();
    $("form#registration input[name='zipcode']").keyup(function() {
        if($(this).val().match(/^\d{4}$/)) {
            $("form#registration img.ajaxloader").show();
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#registration input[name='location']").val(result);
            }).fail(function(result) {
                $("form#registration input[name='location']").val("Ukjent postnummer");
                $("form#registration div.control-group.zipcode").addClass('error');
            }).always(function(result) {
                $("form#registration img.ajaxloader").hide();
            });
        } else {
            $("form#registration input[name='location']").val("");
        }
    });
    $("form#registration input[name='zipcode']").keyup();

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

    $("form#registration input[name='address']").focusout(function() {
        if($(this).val() == "") {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#registration input[name='zipcode']").focusout(function() {
        if(!$(this).val().match(/\d{4}/)) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#registration input[name='phone']").focusout(function() {
        if($(this).val() != "" && ($(this).val().length < 8 || $(this).val().match(/[a-z]/i))) {
            $(this).parents("div.control-group").addClass('error');
        }
    });

    $("form#registration input[name='email']").focusout(function() {
        if($(this).val() != "" && !$(this).val().match(/.+@.+\..+/)) {
            // Email provided, but invalid
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
