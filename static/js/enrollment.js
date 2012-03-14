$(document).ready(function() {

    $("form#registration input[name='zipcode']").keyup(function() {
        if($(this).val().match(/^\d{4}$/)) {
            $.ajax({
                url: '/innmelding/stedsnavn/' + encodeURIComponent($(this).val()) + '/',
                type: 'POST'
            }).done(function(result) {
                $("form#registration input[name='city']").val(result);
            }).fail(function(result) {
                $("form#registration input[name='city']").val("Ukjent postnummer");
            });
        } else {
            $("form#registration input[name='city']").val("");
        }
    });

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
    }).change(function() {
        // We consider year of birth, not date.
        // So in March 2012, someone born December 2011 would be considered 1 year old.
        var age = new Date().getFullYear() - $(this).datepicker('getDate').getFullYear();
        if(age > 26) {
            $("form#registration span.membershiptype").text("Medlemstype: Hovedmedlem");
        } else if(age <= 26 && age >= 19) {
            $("form#registration span.membershiptype").text("Medlemstype: Student/ungdom (19-26 år)");
        } else if(age <= 18 && age >= 13) {
            $("form#registration span.membershiptype").text("Medlemstype: Skoleungdom (13-18 år)");
        } else if(age < 13 ) {
            $("form#registration span.membershiptype").text("Medlemstype: Barn (under 13 år)");
        }
    });

});
