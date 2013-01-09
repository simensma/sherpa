(function(ImageCarouselWidgetEditor, $, undefined ) {

    /* Private variables */

    var currentIndex = 0;
    var imageList = [];
    var newWidgetParentWidth = 0;
    var widget_editor; // Will be set in the document.ready block further down

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
        widget_editor.find("input[name='ratio']").each(function(){
            if($(this).val() == imageList[currentIndex].ratio){
                $(this).attr("checked", "checked");
            }
        });

        widget_editor.find("label[name='sequence']").text("Bilde " + (currentIndex+1) + "/" + imageList.length + " ");
        widget_editor.find("input[name='url']").val(removeImageSizeFromUrl(imageList[currentIndex].url));
        widget_editor.find("input[name='description']").val(imageList[currentIndex].description);
        widget_editor.find("input[name='photographer']").val(imageList[currentIndex].photographer);

        if(imageList[currentIndex].url.trim().length < 1){
            var def = widget_editor.find("img[name='preview']").attr("default");
            widget_editor.find("img[name='preview']").attr('src', def);
            widget_editor.find("div#preview").hide();
        }else{
            widget_editor.find("img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
            widget_editor.find("div#preview").show();
        }

        if(currentIndex == imageList.length -1){
            widget_editor.find("button.next").text(" Nytt bilde");
            widget_editor.find("button.next").prepend("<i class='icon-plus'></i>");
        }else{
            widget_editor.find("button.next").text("Neste bilde ")
            widget_editor.find("button.next").append("<i class='icon-chevron-right'></i>");
        }

        //hax, the onload function is for when you are changing images and the selector needs a new height
        widget_editor.find("img[name='preview']").imagesLoaded(function(){
            openImageCropper(widget_editor.find("img[name='preview']"), widget_editor, imageList[currentIndex].selection);
            setCarouselRatio(imageList[currentIndex].selection == undefined);
            if(imageList[currentIndex].url.trim().length < 1){
                currentCropperInstance.cancelSelection();
            }
        });
    }

    /* Public methods */

    ImageCarouselWidgetEditor.listImages = function(parentWidth) {
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

    ImageCarouselWidgetEditor.saveCropping = function() {
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

    ImageCarouselWidgetEditor.validateContent = function() {
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
        return {
            widget: "carousel",
            images: imageList
        };
    }

    /* Preparations and events */

    $(document).on('widget.edit', 'div.widget.carousel', function() {
        widgetBeingEdited = $(this);
        widget_editor.modal();
        ImageCarouselWidgetEditor.listImages();
    });

    $(document).ready(function() {

        widget_editor = $("div.widget-editor[data-widget='carousel']");
        widget_editor.find("div#ratio-radio").append(getRatioRadioButtons());

        //carousel, stop spinning
        $('.carousel').each(function(){
            $(this).carousel({
                interval:false
            });
        });

        // carousel navigation
        widget_editor.find("button.previous").click(function() {
            ImageCarouselWidgetEditor.saveCropping();
            if(currentIndex > 0){
                currentIndex--;
            }
            displayCurrentImage();
        });
        widget_editor.find("button.next").click(function() {
            ImageCarouselWidgetEditor.saveCropping();
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
        widget_editor.find("button[name='remove']").click(function(){
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
        widget_editor.find("button[name='choose']").click(function(){
            chooseImagefromArchive(chooseFromSpurce);
        });

        //upload clicked
        widget_editor.find("button[name='upload']").click(function(){
            openImageUpload(chooseFromSpurce);
        });

        //updating data in "model" on key up
        widget_editor.find("input[name='url']").keyup(function(){
            imageList[currentIndex].url = $(this).val().trim();
            imageList[currentIndex].selection = undefined;
            widget_editor.find("img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
        });
        widget_editor.find("input[name='description']").keyup(function(){
            imageList[currentIndex].description = $(this).val().trim();
        });
        widget_editor.find("input[name='photographer']").keyup(function(){
            imageList[currentIndex].photographer = $(this).val().trim();
        });

        //ratio
        widget_editor.find("input[name='ratio']").change(function(){
            imageList[currentIndex].ratio = widget_editor.find("input[name='ratio']:checked").val();
            setCarouselRatio(true);
        });

    });

}(window.ImageCarouselWidgetEditor = window.ImageCarouselWidgetEditor || {}, jQuery ));

