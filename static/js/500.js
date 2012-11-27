$(document).ready(function() {
    $("div.plax img.background").plaxify({"xRange": 15, "yRange": 15})
    $("div.plax p.description").plaxify({"xRange": 20, "yRange": 20, "invert": true})
    $("div.plax h1").plaxify({"xRange": 20, "yRange": 25})
    $("div.plax p.photographer").plaxify({"xRange": 15, "yRange": 15})
    $.plax.enable();

    $("a.refresh").click(function() {
        document.location.reload(true);
    });
});
