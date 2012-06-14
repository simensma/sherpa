$(document).ready(function() {

    $("form.placement input.date").each(function() {
        $(this).datepicker({
            changeMonth: true,
            changeYear: true,
            firstDay: 1,
            yearRange: "-1:+20",
            dateFormat: 'dd.mm.yy',
            dayNames: ['Søndag', 'Mandag', 'Tirsdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lørdag'],
            dayNamesShort: ['Søn', 'Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør'],
            dayNamesMin: ['Sø', 'Ma', 'Ti', 'On', 'To', 'Fr', 'Lø'],
            monthNames: ['Januar', 'Februar', 'Mars', 'April', 'Mai', 'Juni', 'Juli', 'August',
              'September', 'Oktober', 'November', 'Desember'],
            monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt',
              'Nov', 'Des'],
            showOn: 'both',
            buttonImage: '/static/img/calendar.png',
            buttonImageOnly: true,
            buttonText: 'Velg dato...'
        });
    });

});

function uploadComplete(result) {
    if(result == 'success') {
        location.reload(true);
    } else if(result == 'parse_error') {
        // TODO
    } else if(result == 'no_files') {
        // TODO
    }
}
