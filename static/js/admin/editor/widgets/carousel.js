(function(ImageCarouselWidget, $, undefined ) {

    /* Private variables */

    var currentIndex = 0;
    var imageList = [];
    var newWidgetParentWidth = 0;

    /* Private methods */

    function setCarouselRatio(change){
        var rat = imageList[currentIndex].ratio.split(":");
        var setWidth = parseInt(rat[0]);
        var setHeight = parseInt(rat[1])
        setImageCropperRatio(setWidth, setHeight, change);
    }

    function chooseFromSpurce(url, description, photographer){
        imageList[currentIndex].url = url;
        imageList[currentIndex].selection = undefined;
        imageList[currentIndex].description = description;
        imageList[currentIndex].photographer = photographer;
        displayCurrentImage();
    }

    function displayCurrentImage() {
        if(currentCropperInstance != undefined){
            currentCropperInstance.cancelSelection();
        }

        if(imageList[currentIndex].ratio == undefined){
            if(currentIndex == 0){
                imageList[currentIndex].ratio = DEFAULT_CAROUSEL_CROP_RATIO;
            }else{
                imageList[currentIndex].ratio = imageList[currentIndex-1].ratio
            }
        }
        $("div.widget-edit[data-widget='carousel'] input[name='ratio']").each(function(){
            if($(this).val() == imageList[currentIndex].ratio){
                $(this).attr("checked", "checked");
            }
        });

        $("div.widget-edit[data-widget='carousel'] label[name='sequence']").text("Bilde " + (currentIndex+1) + "/" + imageList.length + " ");
        $("div.widget-edit[data-widget='carousel'] input[name='url']").val(removeImageSizeFromUrl(imageList[currentIndex].url));
        $("div.widget-edit[data-widget='carousel'] input[name='description']").val(imageList[currentIndex].description);
        $("div.widget-edit[data-widget='carousel'] input[name='photographer']").val(imageList[currentIndex].photographer);

        if(imageList[currentIndex].url.trim().length < 1){
            var def = $("div.widget-edit[data-widget='carousel'] img[name='preview']").attr("default");
            $("div.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', def);
            $("div.widget-edit[data-widget='carousel'] div#preview").hide();
        }else{
            $("div.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
            $("div.widget-edit[data-widget='carousel'] div#preview").show();
        }

        if(currentIndex == imageList.length -1){
            $("div.widget-edit button.next").text(" Nytt bilde");
            $("div.widget-edit button.next").prepend("<i class='icon-plus'></i>");
        }else{
            $("div.widget-edit button.next").text("Neste bilde ")
            $("div.widget-edit button.next").append("<i class='icon-chevron-right'></i>");
        }

        //hax, the onload function is for when you are changing images and the selector needs a new height
        $("div.widget-edit[data-widget='carousel'] img[name='preview']").imagesLoaded(function(){
            openImageCropper($("div.widget-edit[data-widget='carousel'] img[name='preview']"), $("div.widget-edit[data-widget='carousel']"), imageList[currentIndex].selection);
            setCarouselRatio(imageList[currentIndex].selection == undefined);
            if(imageList[currentIndex].url.trim().length < 1){
                currentCropperInstance.cancelSelection();
            }
        });
    }

    /* Public methods */

    ImageCarouselWidget.listImages = function(parentWidth) {
        currentIndex = 0;
        newWidgetParentWidth = 0;

        var ratioWidth = 0;
        var ratioHeight = 0;

        if(widgetBeingEdited == undefined){
            newWidgetParentWidth = parentWidth;
            imageList = [{
                url:"",
                description:"",
                photographer:""
            }];
        }else{
            var widget = JSON.parse(widgetBeingEdited.attr('data-json'));
            imageList = widget.images;
            ratioWidth = widget.ratioWidth;
            ratioHeight = widget.ratioHeight
        }
        displayCurrentImage();
    }

    ImageCarouselWidget.saveCropping = function() {
        var parentWidth = 0;
        if(widgetBeingEdited == undefined){
            parentWidth = newWidgetParentWidth;
        }else{
            parentWidth = widgetBeingEdited.width();
        }

        addCssCropping(parentWidth, function(cssMap, selection, parentHeight){
            if(cssMap == undefined){
                imageList[currentIndex].style = "width:100%;";
                imageList[currentIndex].selection = undefined;
                imageList[currentIndex].parentHeight = undefined;
                imageList[currentIndex].url = addImageSizeToUrl(imageList[currentIndex].url, bestSizeForImage(parentWidth));
                return;
            }

            var style = "";
            for(var key in cssMap) {
                if(cssMap.hasOwnProperty(key)){
                    style += key + ":" + cssMap[key] + ";";
                }
            }
            imageList[currentIndex].style = style;
            imageList[currentIndex].selection = selection;
            imageList[currentIndex].parentHeight = parentHeight;
            imageList[currentIndex].url = addImageSizeToUrl(imageList[currentIndex].url, bestSizeForImage(parentWidth * (parseFloat(cssMap["width"].replace("%", ""))/100) ));
        });
    }

    ImageCarouselWidget.validateContent = function() {
        var numImages = 0;
        for(var i = 0; i < imageList.length; i++){
            if(imageList[i].url.trim().length > 0){
                numImages++;
            }
        }
        if(numImages < 1){
            alert("Du må legge til minst ett bilde(og helst flere, hvis ikke kunne du brukt bildeelementet)");
            return false;
        }
        for(var i = 0; i < imageList.length; i++){
            if(imageList[i].url.trim().length < 1){
                imageList.splice(i, 1);
            }
        }
        return JSON.stringify({
            widget: "carousel",
            images: imageList
        });
    }

    /* Preparations and events */

    $(document).ready(function() {

        $("div.widget-edit[data-widget='carousel'] div#ratio-radio").append(getRatioRadioButtons());

        //carousel, stop spinning
        $('.carousel').each(function(){
            $(this).carousel({
                interval:false
            });
        });

        // carousel navigation
        $("div.widget-edit button.previous").click(function() {
            ImageCarouselWidget.saveCropping();
            if(currentIndex > 0){
                currentIndex--;
            }
            displayCurrentImage();
        });
        $("div.widget-edit button.next").click(function() {
            ImageCarouselWidget.saveCropping();
            if(currentIndex == imageList.length -1){
                //another image is added if you are at the last image and the current image isn't a blank
                if(imageList[currentIndex].url.trim().length > 0){
                    imageList.push({
                        url:"",
                        description:"",
                        photographer:""
                    });
                    currentIndex++;
                }
            }else{
                currentIndex++;
            }
            displayCurrentImage();
        });

        //remove clicked
        $("div.widget-edit[data-widget='carousel'] button[name='remove']").click(function(){
            imageList.splice(currentIndex, 1);
            if(currentIndex > 0){
                currentIndex--;
            }
            //if the user just deleted the only image, fill it with blanks
            if(imageList.length <= 0){
                imageList.push({
                    url:"",
                    description:"",
                    photographer:""
                });
                currentIndex = 0;
            }
            displayCurrentImage();
        });

        //choose clicked
        $("div.widget-edit[data-widget='carousel'] button[name='choose']").click(function(){
            chooseImagefromArchive(chooseFromSpurce);
        });

        //upload clicked
        $("div.widget-edit[data-widget='carousel'] button[name='upload']").click(function(){
            openImageUpload(chooseFromSpurce);
        });

        //updating data in "model" on key up
        $("div.widget-edit[data-widget='carousel'] input[name='url']").keyup(function(){
            imageList[currentIndex].url = $(this).val().trim();
            imageList[currentIndex].selection = undefined;
            $("div.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
        });
        $("div.widget-edit[data-widget='carousel'] input[name='description']").keyup(function(){
            imageList[currentIndex].description = $(this).val().trim();
        });
        $("div.widget-edit[data-widget='carousel'] input[name='photographer']").keyup(function(){
            imageList[currentIndex].photographer = $(this).val().trim();
        });

        //ratio
        $("div.widget-edit[data-widget='carousel'] input[name='ratio']").change(function(){
            imageList[currentIndex].ratio = $("div.widget-edit[data-widget='carousel'] input[name='ratio']:checked").val();
            setCarouselRatio(true);
        });

    });

}(window.ImageCarouselWidget = window.ImageCarouselWidget || {}, jQuery ));

