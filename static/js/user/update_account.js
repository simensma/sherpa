$(document).ready(function() {

    $("input[name='dob']").pickadate({
        format: 'dd.mm.yyyy',
        yearSelector: true,
        monthSelector: true
    });

});
