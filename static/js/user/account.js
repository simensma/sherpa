$(document).ready(function() {
    $("a.sync-memberinfo").click(function() {
        $(this).hide();
        $("p.sync-loading").show();
        $.ajax({
            url: '/minside/synkroniser/'
        }).done(function() {
            document.location.reload(true);
        }).fail(function() {
            alert("Beklager, det oppstod en teknisk feil ved synkronisering. Feilen har blitt logget og vi vil fikse feilen så snart vi kan. Vennligst prøv igjen senere.");
            $("a.sync-memberinfo").show();
            $("p.sync-loading").hide();
        });
    });
});
