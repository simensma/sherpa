$(document).ready(function() {

    $("form#registration input[name='zipcode']").keyup(function() {
        if($(this).val().match(/^\d{4}$/)) {
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#registration input[name='location']").val(result);
            }).fail(function(result) {
                $("form#registration input[name='location']").val("Ukjent postnummer");
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
        buttonText: 'Velg dato...'
    });

    $("form#registration button[value='done']").click(function(event) {
        if($("form#registration input[name='name']").val() == "") {
            // TODO: Assume the user didn't want to add the current form as a member.
            // If it's partly filled out, we should ask whether or not to include this member.
            $("form#registration").append($('<input type="hidden" name="skip" value="true">'));
        }
    });

});
