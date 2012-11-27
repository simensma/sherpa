$(document).ready(function() {
    $("div.plax img.background").plaxify({"xRange": 200, "yRange": 25, "invert": true})
    $("div.plax p").plaxify({"xRange": 20, "yRange": 20})
    $("div.plax h1").plaxify({"xRange": 20, "yRange": 20, "invert": true})
    $.plax.enable();

    $("a.refresh").click(function() {
        document.location.reload(true);
    });
});
