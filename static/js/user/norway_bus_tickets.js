$(document).ready(function() {
    var form = $("form");

    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
    var five_days_from_now = new Date().setDate(now.getDate() + 5);
    var nextYear = new Date(now.getFullYear() + 1, 0, 1, 0, 0, 0, 0);
    form.find("div.control-group.date div.input-append.date").datepicker({
        format: 'dd.mm.yyyy',
        weekStart: 1,
        autoclose: true,
        language: 'nb',
        startDate: today,
        endDate: nextYear,
        forceParse: false
    }).on('changeDate', function(e) {
        if(e.date.valueOf() < five_days_from_now.valueOf()) {
            alert("Det er få dager igjen til avreisedatoen du valgte - vær obs på at vi ikke garantere at du mottar billetten i tide!");
        }
    });

});
