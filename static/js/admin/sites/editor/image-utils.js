//the default and the first of the predefines should(must) be the same
var PREDEFINED_CROP_RATIOS = {
    Fri:"0:0",
    Widescreen:"16:9",
    Landskap:"12:8",
    Portrett:"3:4",
    Kvadrat:"1:1"
};
var DEFAULT_CAROUSEL_CROP_RATIO = PREDEFINED_CROP_RATIOS.Widescreen;
var DEFAULT_CROP_RATIO = PREDEFINED_CROP_RATIOS.Fri;

function getRatioRadioButtons() {
    var ratioradio = "<table><tr>";
    var r = PREDEFINED_CROP_RATIOS;
    for(var key in r) {
        if(r.hasOwnProperty(key)) {
            ratioradio += "<td><input type='radio' name='ratio' value='" + r[key] + "'> " + key + " </td>";
        }
    }
    ratioradio += "</tr></table>";
    return ratioradio;
}
