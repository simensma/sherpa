$(document).ready(function() {

    $("div.multiedit").hide();
    function toggleMultiedit() {
        if($("#archive-gallery li.selected").length > 0) {
            $("div.multiedit").show();
        } else {
            $("div.multiedit").hide();
        }
    }

    $("#archive-gallery li.album button.mark").click(function() {
        $("#archive-gallery li.image.selected").removeClass('selected');
        $(this).parent("li").toggleClass('selected');
        toggleMultiedit();
    });

    $("#archive-gallery li.image button.mark").click(function() {
        $("#archive-gallery li.album.selected").removeClass('selected');
        $(this).parent("li").toggleClass('selected');
        toggleMultiedit();
    });

});
