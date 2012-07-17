var imagePickedCallback; // Called when an image is picked in the dialog
var imageRemovedCallback; // Called when an image is removed, from the dialog
var currentImage;
var cancelRequested;
var firstOpen;

var imageCurrentRatioWidth = 0;
var imageCurrentRatioHeight = 0;

$(document).ready(function() {

    var ratioradio = "<table><tr>";
    var r = PREDEFINED_CROP_RATIOS;
    var first = "id='default'";
    for(var key in r) {
        if(r.hasOwnProperty(key)){
            ratioradio += "<td><input type='radio' " + first + " name='ratio' value=" + r[key] + "> " + key + " </td>";
            first = "";
        }
    }
    ratioradio += "</tr></table>";
    $("div#dialog-change-image div#ratio-radio").append(ratioradio);

    $("div#dialog-change-image").parent().find("a.ui-dialog-titlebar-close").click(function() {
        if(firstOpen){
            currentCropperInstance.cancelSelection();
            imageRemovedCallback();
        }
    });

    $("div#dialog-change-image button.choose-image").click(function() {
        chooseImagefromArchive(inputDataFromSource);
    });
    $("div#dialog-change-image button.upload-image").click(function() {
        openImageUpload(inputDataFromSource);
    });

    function inputDataFromSource(url, description, photographer){

        $("div#dialog-change-image div.preview-container").show();

        $("div#dialog-change-image input[name='src']").val(removeImageSizeFromUrl(url));
        $("div#dialog-change-image input[name='description']").val(description);
        $("div#dialog-change-image input[name='photographer']").val(photographer);
        $("div#dialog-change-image img.preview").attr('src', addImageSizeToUrl(url, IMAGE_PPREVIEW_WIDTH));

        currentCropperInstance.cancelSelection();
        $("div#dialog-change-image").imagesLoaded(function(){
            openImageCropper($("div#dialog-change-image img.preview"), $("div#dialog-change-image"), undefined);
            setImageRatio(true);
        });
        openImageCropper($("div#dialog-change-image img.preview"), $("div#dialog-change-image"), undefined);
        setImageRatio(true);
    }

    $("div#dialog-change-image input[name='src']").keyup(function() {
        $("div#dialog-change-image div.preview-container").show();
        $("div#dialog-change-image img.preview").attr('src', addImageSizeToUrl($(this).val(), IMAGE_PPREVIEW_WIDTH));
        currentCropperInstance.cancelSelection();
        setImageRatio(true);
    });

    $("div#dialog-change-image button.insert-image").click(function() {

        var dialog = $(this).parents("div#dialog-change-image");
        var src = dialog.find("input[name='src']").val();
        if(src == "") {
            $("div#dialog-change-image div.empty-src").show();
            return;
        }
        $("div#dialog-change-image div.empty-src").hide();

        var parentWidth = currentImage.parent().width();

        addCssCropping(parentWidth, function(cssMap, selection, parentHeight){
            var image = currentImage;
            var wrapper = currentImage.parent();

            var newurl = $("div#dialog-change-image input[name='src']").val()

            if(cssMap != undefined){
                src = addImageSizeToUrl(newurl, bestSizeForImage(parentWidth * (parseFloat(cssMap["width"].replace("%", ""))/100)));
                image.css(cssMap);
                image.attr("data-selection", JSON.stringify(selection));
                image.attr("data-parentHeight", parentHeight);
                wrapper.css("height", parentHeight+"px");
            }else{
                src = addImageSizeToUrl(newurl, bestSizeForImage(parentWidth));
                image.removeAttr("style");
                image.removeAttr("data-selection");
                image.removeAttr("data-parentHeight");
                image.css("width", "100%");
                wrapper.css("height", "auto");
            }
        });

        currentImage.attr("data-ratio-width", imageCurrentRatioWidth);
        currentImage.attr("data-ratio-height", imageCurrentRatioHeight);

        currentCropperInstance.cancelSelection();
        dialog.dialog('close');

        var anchor = dialog.find("input[name='anchor']");
        if(anchor.length > 0) {
            anchor = anchor.val();
            if(anchor.length != 0 && !anchor.match(/^https?:\/\//)) {
                anchor = "http://" + anchor;
            }
        } else {
            anchor = '';
        }

        var description = dialog.find("input[name='description']").val();
        var photographer = dialog.find("input[name='photographer']").val();
        imagePickedCallback(src, anchor, description, photographer);
    });

    $("div#dialog-change-image button.remove-image").click(function() {
        currentCropperInstance.cancelSelection();
        $(this).parents("div#dialog-change-image").dialog('close');
        imageRemovedCallback();
    });

    $("div#dialog-change-image input[name='ratio']").change(function(){
        setImageRatio(true);
    });
});

function openImageDialog(image, anchor, description, photographer, saveCallback, removeCallback) {
    firstOpen = false;
    currentImage = image;
    imagePickedCallback = saveCallback;
    imageRemovedCallback = removeCallback;

    var src = removeImageSizeFromUrl(image.attr("src"));

    $("div#dialog-change-image div.image-details").show();
    $("div#dialog-change-image div.empty-src").hide();
    $("div#dialog-change-image img.preview").attr('src', addImageSizeToUrl(src, IMAGE_PPREVIEW_WIDTH));

    var dialog = $("div#dialog-change-image");
    dialog.dialog('open');

    dialog.find("input[name='src']").val(src);
    if(anchor !== undefined) {
        dialog.find("input[name='anchor']").val(anchor);
        dialog.find("tr.anchor").show();
    } else {
        dialog.find("tr.anchor").hide();
    }
    if(description !== undefined) {
        dialog.find("input[name='description']").val(description);
        dialog.find("tr.description").show();
    } else {
        dialog.find("tr.description").hide();
    }
    if(photographer !== undefined) {
        dialog.find("input[name='photographer']").val(photographer);
        dialog.find("tr.photographer").show();
    } else {
        dialog.find("tr.photographer").hide();
    }

    var sel = image.attr("data-selection");
    if(sel == undefined || sel == ""){
        sel = undefined;
    }else{
        sel = JSON.parse(sel);
    }

    var ratioW = image.attr("data-ratio-width");
    var ratioH = image.attr("data-ratio-height");
    if(ratioIsValid(ratioW, ratioH)){
        //select correct ratiio-radio
        var chosenRatio = ratioW + ":" + ratioH;
        $("div#dialog-change-image input[name='ratio']").each(function(){
            if($(this).val() == chosenRatio){
                $(this).attr("checked", "checked");
            }
        });
    }else{
        $("div#dialog-change-image input[name='ratio'][value='" + DEFAULT_CROP_RATIO +"']").attr("checked", "checked");
    }

    $("div#dialog-change-image").imagesLoaded(function(){
        openImageCropper($("div#dialog-change-image img.preview"), dialog, sel);
        setImageRatio((sel == undefined));
        if(src.trim().length < 1){
            $("div#dialog-change-image div.preview-container").hide();
            currentCropperInstance.cancelSelection();
        }
    });

    //hax for preventing saving of empty image and crash of database as result
    if(src.trim().length < 1){
        firstOpen = true;
        imagePickedCallback("http://www.turistforeningen.no/static/img/placeholder.png", "", "", "");
    }
}

function setImageRatio(change){
    try{
        var checked = $("div#dialog-change-image input[name='ratio']:checked").val().split(":");
        imageCurrentRatioWidth = parseInt(checked[0])
        imageCurrentRatioHeight = parseInt(checked[1]);
    }catch(e){
        imageCurrentRatioWidth = 0;
        imageCurrentRatioHeight = 0;
    }

    if(ratioIsValid(imageCurrentRatioWidth, imageCurrentRatioHeight)){
        setImageCropperRatio(imageCurrentRatioWidth, imageCurrentRatioHeight, change);
    }else{
        setImageCropperRatio(0, 0, change);
    }
}