var LOCAL_IMAGE_PREFIX = "cdn.turistforeningen.no";
var THUMB_SIZES = [1880, 940, 500, 150];
var IMAGE_PPREVIEW_WIDTH = 940;

//the default and the first of the predefines should(must) be the same
var PREDEFINED_CROP_RATIOS = {
    Fri:"0:0",
    Widescreen:"16:9",
    Landskap:"12:8",
    Portrett:"3:4",
    Firkant:"1:1"
};
var DEFAULT_CAROUSEL_CROP_RATIO = PREDEFINED_CROP_RATIOS.Widescreen;
var DEFAULT_CROP_RATIO = PREDEFINED_CROP_RATIOS.Fri;

var DEFAULT_IMAGE = "http://www.turistforeningen.no/static/img/placeholder.png";

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

function addImageSizeToUrl(url, size) {
    //if url not from turistforeningen, do nothing
    if(url.indexOf(LOCAL_IMAGE_PREFIX) < 0) {
        return url;
    }

    //if the url has a -size in it, ignore it and use our own size instead, this could happen if the user explicitly types in an url with -size, or old images
    url = url.replace(/-\d+/g, "");

    //the requested size is the original size
    if(size === undefined) {
        return url;
    }

    var parts = url.split(".");
    var newurl = parts[0];
    for(var i = 1; i< parts.length-1; i++) {
        newurl += "." + parts[i];
    }
    newurl += "-" + size + "." + parts[parts.length-1];
    return newurl;
}

function removeImageSizeFromUrl(url) {
    if(url.indexOf(LOCAL_IMAGE_PREFIX) < 0) {
        return url;
    }
    return url.replace(/-\d+/g, '');
}

function bestSizeForImage(displayWidth) {
    for(var i = THUMB_SIZES.length-1; i >= 0; i--) {
        if(THUMB_SIZES[i] >= displayWidth) {
            return THUMB_SIZES[i];
        }
    }
    return undefined;
}

function ratioIsValid(width, height) {
    var r = width/height;
    if(!isNaN(r) && width > 0 && height > 0) {
        return true;
    }
    return false;
}
