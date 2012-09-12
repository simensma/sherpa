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

    $("table.placements tr.placement").click(function() {
        var form = $("div.placement-dialog form");
        form.find("input[name='id']").val($(this).attr('data-id'));
        form.find("select[name='ad'] option[value='" + $(this).attr('data-ad') + "']").prop('selected', true);
        form.find("input[name='start_date']").val($(this).attr('data-start-date'));
        form.find("input[name='end_date']").val($(this).attr('data-end-date'));
    });

    $("table.ads td.ad").click(function() {
        var form = $("div.ad-dialog form");
        form.find("input[name='id']").val($(this).attr('data-id'));
        form.find("input[name='name']").val($(this).attr('data-name'));
        form.find("input[name='destination']").val($(this).attr('data-destination'));
        form.find("input[name='width']").val($(this).attr('data-width'));
        form.find("input[name='height']").val($(this).attr('data-height'));
    });
});
