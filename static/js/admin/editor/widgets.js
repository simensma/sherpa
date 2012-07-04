/* Editing widgets */
$(document).ready(function() {

    //carousel, stop spinning
    $('.carousel').each(function(){
        $(this).carousel({
            interval:false
        });
    });
    
    // Save any widget
    $("div.dialog.widget-edit button.save").click(function() {
        var content = validateContent($(this).parents("div.dialog.widget-edit"));
        if(content === false) {
            return $(this);
        }
        $("div.dialog.widget-edit").dialog('close');
        saveWidget(content);
    });

    // Remove any widget
    $("div.dialog.widget-edit button.remove").click(function() {
        $(this).parents(".dialog").dialog('close');
        if(widgetBeingEdited != undefined){
            removeContent(widgetBeingEdited);
        }
    });

    //the code below in the readyfunction is the carousel
    //navigation
    $("div.dialog.widget-edit button.previous").click(function() {
        saveCropping();
        if(currentIndex > 0){
            currentIndex--;
        }
        displayCurrentImage();
    });
    $("div.dialog.widget-edit button.next").click(function() {
        saveCropping();
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
    $("div.dialog.widget-edit[data-widget='carousel'] button[name='remove']").click(function(){
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
    $("div.dialog.widget-edit[data-widget='carousel'] button[name='choose']").click(function(){
        chooseImagefromArchive(function(url, description, photographer){
            imageList[currentIndex].url = url;
            imageList[currentIndex].selection = undefined;
            imageList[currentIndex].description = description;
            imageList[currentIndex].photographer = photographer;
            displayCurrentImage();
        });
    });

    //updating data in "model" on key up
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='url']").keyup(function(){
        imageList[currentIndex].url = $(this).val().trim();
        imageList[currentIndex].selection = undefined;
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', imageList[currentIndex].url);
    });
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='description']").keyup(function(){
        imageList[currentIndex].description = $(this).val().trim();
    });
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='photographer']").keyup(function(){
        imageList[currentIndex].photographer = $(this).val().trim();
    });

    //ratio
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='ratio-width']").keyup(function(){
        currentRatioWidth = parseInt($(this).val().trim());
        setRatio();
    });
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='ratio-height']").keyup(function(){
        currentRatioHeight = parseInt($(this).val().trim());
        setRatio();
    });
});

function saveWidget(content){
    if(widgetBeingEdited !== undefined) {
        enableOverlay();
        $.ajaxQueue({
            url: '/sherpa/cms/widget/oppdater/' + widgetBeingEdited.attr('data-id') + '/',
            data: 'content=' + encodeURIComponent(content)
        }).done(function(result) {
            result = JSON.parse(result);
            widgetBeingEdited.contents().remove();
            widgetBeingEdited.append(result.content);
            widgetBeingEdited.attr('data-json', result.json);
            disableIframes(widgetBeingEdited);
        }).always(function() {
            disableOverlay();
        });
    } else {
        addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column, widgetPosition.order, content, 'widget', function(wrapper) {
                refreshSort();
                removeEmpties();
                setEmpties();
        });
    }
}

function setRatio(){
    var r = currentRatioWidth/currentRatioHeight;
    if(!isNaN(r) && currentRatioWidth > 0 && currentRatioHeight > 0){
        setImageCropperRatio(currentRatioWidth, currentRatioHeight);
    }else{
        setImageCropperRatio(0, 0);
    }
}

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return JSON.stringify({
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        });
    } else if(widget.attr('data-widget') == 'carousel') {
        saveCropping();
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
    } else if(widget.attr('data-widget') == 'articles') {
        var count = widget.find("input[name='count']").val();
        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall artikler som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst én artikkel!");
            return false;
        }
        return JSON.stringify({
            widget: "articles",
            count: count
        });
    } else if(widget.attr('data-widget') == 'blog') {
        var count = widget.find("input[name='count']").val();
        var category = widget.find("select[name='category']").val();

        if(isNaN(Number(count))) {
            alert("Du må angi et tall for antall blogginnlegg som skal vises!");
            return false;
        } else if(count < 1) {
            alert("Du må vise minst ett blogginnlegg!");
            return false;
        }
        return JSON.stringify({
            widget: "blog",
            count: count,
            category : category
        });
    } else if(widget.attr('data-widget') == 'embed') {
        var code = widget.find("textarea[name='code']").val();
        if(code == '') {
            alert("Du må jo legg inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, trykk på 'Slett widget'-knappen.");
            return false;
        }
        return JSON.stringify({
            widget: "embed",
            code: code
        });
    }
}

function openWidgetDialog(type, parentWidth){
    if(type == 'carousel') {
        listImages(parentWidth);
    }
}

function editWidget() {
    widgetBeingEdited = $(this);
    var widget = JSON.parse($(this).attr('data-json'));
    $("div.dialog.widget-edit[data-widget='" + widget.widget + "']").dialog('open');
    if(widget.widget == 'quote') {
        $("div.dialog.widget-edit[data-widget='quote'] textarea[name='quote']").val(widget.quote);
        $("div.dialog.widget-edit[data-widget='quote'] input[name='author']").val(widget.author);
    } else if(widget.widget == 'articles') {
        $("div.dialog.widget-edit[data-widget='articles'] input[name='count']").val(widget.count);
    } else if(widget.widget == 'blog') {
        $("div.dialog.widget-edit[data-widget='blog'] input[name='count']").val(widget.count);
        $("div.dialog.widget-edit[data-widget='blog'] select[name='category']").val(widget.category);
    } else if(widget.widget == 'embed') {
        $("div.dialog.widget-edit[data-widget='embed'] textarea[name='code']").text(widget.code);
    }else if(widget.widget == 'carousel') {
        listImages();
    }
}

function displayCurrentImage(){
    if(currentCropperInstance != undefined){
        currentCropperInstance.cancelSelection();
    }

    $("div.dialog.widget-edit[data-widget='carousel'] label[name='sequence']").text("Bilde " + (currentIndex+1) + "/" + imageList.length + " ");
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='url']").val(imageList[currentIndex].url);
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='description']").val(imageList[currentIndex].description);
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='photographer']").val(imageList[currentIndex].photographer);
    
    if(imageList[currentIndex].url.trim().length <= 1){
        var def = $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr("default");
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', def);
    }else{
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', imageList[currentIndex].url);
    }

    if(currentIndex == imageList.length -1){
        $("div.dialog.widget-edit button.next").text(" Nytt bilde");
        $("div.dialog.widget-edit button.next").prepend("<i class='icon-plus'></i>");
    }else{
        $("div.dialog.widget-edit button.next").text("Neste bilde ")
        $("div.dialog.widget-edit button.next").append("<i class='icon-chevron-right'></i>");
    }

    //hax, the onload function is for when you are changing images and the selector needs a new height
    $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").load(function(){
        openImageCropper($("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']"), $("div.dialog.widget-edit[data-widget='carousel']"), imageList[currentIndex].selection);
        setRatio();
    });
    //the load dosent load on the first item for some reasopn, needs this :(
    openImageCropper($("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']"), $("div.dialog.widget-edit[data-widget='carousel']"), imageList[currentIndex].selection);
    setRatio();
}

var currentIndex = 0;
var imageList = [];
var currentRatioWidth = 0;
var currentRatioHeight = 0;
var newWidgetParentWidth = 0;

function listImages(parentWidth){
    currentIndex = 0;
    newWidgetParentWidth = 0;
    try{
        currentRatioWidth = parseInt($(this).val().trim());
        currentRatioHeight = parseInt($(this).val().trim());
    }catch(e){
        currentRatioWidth = 0;
        currentRatioHeight = 0;
    }

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
    }
    displayCurrentImage();
}

function saveCropping(){
    var parentWidth = 0;
    if(widgetBeingEdited == undefined){
        parentWidth = newWidgetParentWidth;
    }else{
        parentWidth = widgetBeingEdited.width();
    }

    addCssCropping(parentWidth, function(cssMap, selection, parentHeight){
        if(cssMap == undefined){
            imageList[currentIndex].style = undefined;
            imageList[currentIndex].selection = undefined;
            imageList[currentIndex].parentHeight = undefined;
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
    });
}