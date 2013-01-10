$(document).ready(function() {

    var loadindex = 1;
    var loading = false;
    var cleanslate = false;
    var complete = false;

    var filterminage;
    var filtermaxage;
    var filtergender;
    var filterfylke;

    var wrapper = $("div.wrapper");
    var listwrapper = $("div.annonse-list-wrapper");

    var lowerageselect = $("select.lowerageselect");
    var upperageselect = $("select.upperageselect");
    var genderselect = $("select.genderselect");
    var fylkeselect = $("select.fylkeselect");

    lowerageselect.change(filterChanged);
    upperageselect.change(filterChanged);
    genderselect.change(filterChanged);
    fylkeselect.change(filterChanged);

    function filterChanged(){
        minage = parseInt(lowerageselect.val());
        maxage = parseInt(upperageselect.val());
        //this is some jquery quirk. .val() removes leading zeroes, and focus uses leading zeroes in county codes
        fylke = fylkeselect.attr("value");
        gender = parseInt(genderselect.val());

        filterminage = minage;
        filtermaxage = maxage;
        filterfylke = fylke;
        filtergender = gender;

        loadindex = 0;
        cleanslate = true;
        listwrapper.addClass("hide");

        loadAnnonser();
    }

    $(window).scroll(function() {
        if(!loading && !complete && $(window).scrollTop() + $(window).height() > wrapper.offset().top + wrapper.height()) {
            loadAnnonser();
        }
    });

    function loadAnnonser(){
        loading = true;

        filter = {
            minage:filterminage,
            maxage:filtermaxage,
            gender:filtergender,
            fylke:filterfylke
        }

        $.ajaxQueue({
            url: "/fjelltreffen/load/" + loadindex + "/",
            data: 'filter=' + JSON.stringify(filter)
        }).done(function(result) {
            if(cleanslate){
                listwrapper.empty();
                listwrapper.fadeIn()
            }
            result = JSON.parse(result);
            annonsehtml = result["html"];

            if(annonsehtml.length == 0){
                complete = true;
                if(cleanslate){
                    var noresult = $("<p>Ingen resultater, prøv å søke på noe annet.</p>");
                    noresult.addClass("hide");
                    listwrapper.append(noresult);
                    noresult.fadeIn();
                }
            }else{
                var newitems = $(annonsehtml);
                newitems.addClass("hide");

                listwrapper.append(newitems);
                newitems.fadeIn();
            }
            if(!cleanslate){
                loadindex++;
            }
        }).fail(function(result) {
            if(cleanslate){
                listwrapper.fadeIn();
            }
            alert("Beklager, det oppstod en feil når vi forsøkte å laste flere annonser. Prøv å oppdatere siden, og scrolle ned igjen.");
            complete = true;
        }).always(function(result) {
            loading = false;
            cleanslate = false;
        });
    }
});