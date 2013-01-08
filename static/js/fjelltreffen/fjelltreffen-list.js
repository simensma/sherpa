$(document).ready(function() {

    var loadindex = 1;
    var loading = false;
    var complete = false;

    var wrapper = $("div.wrapper");

    $(window).scroll(function() {
        if(!loading && !complete && $(window).scrollTop() + $(window).height() > wrapper.offset().top + wrapper.height()) {
            loadAnnonser();
        }
    });

    function loadAnnonser(){
        loading = true;

        $.ajaxQueue({
            url: "/fjelltreffen/load/" + loadindex + "/",
        }).done(function(result) {
            result = JSON.parse(result);
            annonsehtml = result["html"];

            if(annonsehtml.length == 0){
                complete = true;
            }

            var newitems = $(annonsehtml);
            newitems.addClass("hide");

            $("div.annonse-list-wrapper").append(newitems);
            newitems.fadeIn();

            loadindex++;
        }).fail(function(result) {
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere annonser. Prøv å oppdatere siden, og scrolle ned igjen.");
            complete = true;
        }).always(function(result) {
            loading = false;
        });
    }
});