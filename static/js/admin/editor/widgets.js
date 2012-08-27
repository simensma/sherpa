
/* Editing widgets */
$(document).ready(function() {

    /* Carousel */

    $("div.dialog.widget-edit[data-widget='carousel'] div#ratio-radio").append(getRatioRadioButtons());

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
        chooseImagefromArchive(chooseFromSpurce);
    });

    //upload clicked
    $("div.dialog.widget-edit[data-widget='carousel'] button[name='upload']").click(function(){
        openImageUpload(chooseFromSpurce);
    });

    function chooseFromSpurce(url, description, photographer){
        imageList[currentIndex].url = url;
        imageList[currentIndex].selection = undefined;
        imageList[currentIndex].description = description;
        imageList[currentIndex].photographer = photographer;
        displayCurrentImage();
    }

    //updating data in "model" on key up
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='url']").keyup(function(){
        imageList[currentIndex].url = $(this).val().trim();
        imageList[currentIndex].selection = undefined;
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
    });
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='description']").keyup(function(){
        imageList[currentIndex].description = $(this).val().trim();
    });
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='photographer']").keyup(function(){
        imageList[currentIndex].photographer = $(this).val().trim();
    });

    //ratio
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='ratio']").change(function(){
        imageList[currentIndex].ratio = $("div.dialog.widget-edit[data-widget='carousel'] input[name='ratio']:checked").val();
        setCarouselRatio(true);
    });

    /* Articles */

    // Enable/disable
    var articles = $("div.dialog.widget-edit[data-widget='articles']");
    articles.find("input[name='tag-link']").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.ajaxQueue({
                url: '/sherpa/bildearkiv/tag/filter/',
                data: 'term=' + encodeURIComponent(query)
            }).done(function(result) {
                process(JSON.parse(result));
            });
        }
    });
    articles.find("input[name='set-tag-link']").change(function() {
        if($(this).is(':checked')) {
            articles.find("input[name='tag-link']").removeAttr('disabled');
        } else {
            articles.find("input[name='tag-link']").attr('disabled', true).val("");
        }
    });

    articles.find("input[name='enable-tags']").change(function() {
        if($(this).is(':checked')) {
            articles.find("input[name='tags']").removeAttr('disabled');
        } else {
            articles.find("input[name='tags']").attr('disabled', true).val("");
            articles.find("div.tag-box").empty();
        }
    });

    // Create the tagger object, make it globally accessible
    window.article_widget_tagger = new Tagger(articles.find("input[name='tags']"), function(tag) {
        // New tag added
        var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + tag + '</div>');
        articles.find("div.tag-box").append(tag);
    }, function(tag) {
        // Existing tag
        articles.find("div.tag-box div.tag").each(function() {
            if($(this).text().trim().toLowerCase() == tag.toLowerCase()) {
                var item = $(this);
                var c = item.css('color');
                var bg = item.css('background-color');
                item.css('color', 'white');
                item.css('background-color', 'red');
                setTimeout(function() {
                    item.css('color', c);
                    item.css('background-color', bg);
                }, 1000);
            }
        });
    });

    // Add events to the tag remover button
    $(document).on('mouseover', "div.dialog.widget-edit[data-widget='articles'] div.tag-box div.tag a", function() {
        $(this).children("img").attr('src', '/static/img/so/close-hover.png');
    });
    $(document).on('mouseout', "div.dialog.widget-edit[data-widget='articles'] div.tag-box div.tag a", function() {
        $(this).children("img").attr('src', '/static/img/so/close-default.png');
    });
    $(document).on('click', "div.dialog.widget-edit[data-widget='articles'] div.tag-box div.tag a", function() {
        article_widget_tagger.removeTag($(this).parent().text().trim());
        $(this).parent().remove();
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

function setCarouselRatio(change){
    var rat = imageList[currentIndex].ratio.split(":");
    var setWidth = parseInt(rat[0]);
    var setHeight = parseInt(rat[1])
    setImageCropperRatio(setWidth, setHeight, change);
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
        var title = widget.find("input[name='title']").val();
        if(widget.find("input[name='set-tag-link']").is(':checked')) {
            var tag_link = widget.find("input[name='tag-link']").val();
        } else {
            var tag_link = null;
        }
        if(widget.find("input[name='enable-tags']:checked").length > 0) {
            var tags = article_widget_tagger.tags;
        } else {
            var tags = [];
        }
        return JSON.stringify({
            widget: "articles",
            title: title,
            tag_link: tag_link,
            tags: tags,
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
            alert("Du må jo legge inn koden du vil bruke først! Hvis du ikke vil bruke widgeten likevel, trykk på 'Slett widget'-knappen.");
            return false;
        }
        return JSON.stringify({
            widget: "embed",
            code: code
        });
    } else if(widget.attr('data-widget') == 'fact') {
        var content = widget.find("div.content").html();
        return JSON.stringify({
            widget: "fact",
            content: content
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
        var articles = $("div.dialog.widget-edit[data-widget='articles']");
        articles.find("input[name='title']").val(widget.title);
        articles.find("input[name='count']").val(widget.count);
        if(widget.tag_link == null) {
            articles.find("input[name='set-tag-link'").removeAttr('checked');
            articles.find("input[name='tag-link']").attr('disabled', true).val("");
        }
        article_widget_tagger.tags = widget.tags;
        var box = articles.find("div.tag-box");
        box.empty();
        for(var i=0; i<widget.tags.length; i++) {
            var tag = $('<div class="tag"><a href="javascript:undefined"><img src="/static/img/so/close-default.png"></a> ' + widget.tags[i] + '</div>');
            box.append(tag);
        }
        if(widget.tags.length > 0) {
            articles.find("input[name='enable-tags']").attr('checked', true);
            articles.find("input[name='tags']").removeAttr('disabled');
        } else {
            articles.find("input[name='enable-tags']").removeAttr('checked');
            articles.find("input[name='tags']").attr('disabled', true);
        }
    } else if(widget.widget == 'blog') {
        $("div.dialog.widget-edit[data-widget='blog'] input[name='count']").val(widget.count);
        $("div.dialog.widget-edit[data-widget='blog'] select[name='category']").val(widget.category);
    } else if(widget.widget == 'embed') {
        $("div.dialog.widget-edit[data-widget='embed'] textarea[name='code']").text(widget.code);
    }else if(widget.widget == 'carousel') {
        listImages();
    } else if(widget.widget == 'fact') {
        $("div.dialog.widget-edit[data-widget='fact'] div.content").html(widget.content);
    }
}

function displayCurrentImage(){
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
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='ratio']").each(function(){
        if($(this).val() == imageList[currentIndex].ratio){
            $(this).attr("checked", "checked");
        }
    });

    $("div.dialog.widget-edit[data-widget='carousel'] label[name='sequence']").text("Bilde " + (currentIndex+1) + "/" + imageList.length + " ");
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='url']").val(removeImageSizeFromUrl(imageList[currentIndex].url));
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='description']").val(imageList[currentIndex].description);
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='photographer']").val(imageList[currentIndex].photographer);

    if(imageList[currentIndex].url.trim().length < 1){
        var def = $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr("default");
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', def);
        $("div.dialog.widget-edit[data-widget='carousel'] div#preview").hide();
    }else{
        $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('src', addImageSizeToUrl(imageList[currentIndex].url, IMAGE_PPREVIEW_WIDTH));
        $("div.dialog.widget-edit[data-widget='carousel'] div#preview").show();
    }

    if(currentIndex == imageList.length -1){
        $("div.dialog.widget-edit button.next").text(" Nytt bilde");
        $("div.dialog.widget-edit button.next").prepend("<i class='icon-plus'></i>");
    }else{
        $("div.dialog.widget-edit button.next").text("Neste bilde ")
        $("div.dialog.widget-edit button.next").append("<i class='icon-chevron-right'></i>");
    }

    //hax, the onload function is for when you are changing images and the selector needs a new height
    $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").imagesLoaded(function(){
        openImageCropper($("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']"), $("div.dialog.widget-edit[data-widget='carousel']"), imageList[currentIndex].selection);
        setCarouselRatio(imageList[currentIndex].selection == undefined);
        if(imageList[currentIndex].url.trim().length < 1){
            currentCropperInstance.cancelSelection();
        }
    });
}

var currentIndex = 0;
var imageList = [];
var newWidgetParentWidth = 0;

function listImages(parentWidth){
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

function saveCropping(){
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