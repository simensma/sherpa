/* Editing widgets */
$(document).ready(function() {

    // Save any widget
    $("div.dialog.widget-edit button.save").click(function() {
        var content = validateContent($(this).parents("div.dialog.widget-edit"));
        if(content === false) {
            return $(this);
        }
        $("div.dialog.widget-edit").dialog('close');
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
            addContent(widgetPosition.prev, widgetPosition.parent, widgetPosition.column,
                widgetPosition.order, content, 'widget', function(wrapper) {
                    refreshSort();
                    removeEmpties();
                    setEmpties();
            });
        }
    });

    // Remove any widget
    $("div.dialog.widget-edit button.remove").click(function() {
        $(this).parents(".dialog").dialog('close');
        removeContent(widgetBeingEdited);
    });

    //carousel nagiation
    $("div.dialog.widget-edit button.previous").click(function() {
        if(currentIndex > 0){
            currentIndex--;
        }
        displayCurrentImage();
    });

    $("div.dialog.widget-edit button.next").click(function() {
        if(currentIndex == imageList.length -1){
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
        console.log(imageList.length);
        imageList.splice(currentIndex, 1);
        if(currentIndex > 0){
            currentIndex--;
        }
        console.log(imageList.length);

        var widget = JSON.parse(widgetBeingEdited.attr('data-json'));
        displayCurrentImage();
        widget.images = imageList;
        widgetBeingEdited.attr('data-json', JSON.stringify(widget));
    });

    //choose clicked
    $("div.dialog.widget-edit[data-widget='carousel'] button[name='choose']").click(function(){
        carouselMode = true;

        openImageDialog(undefined, undefined, undefined, undefined, function(url, description, photographer){
            imageList[currentIndex].url = url;
            imageList[currentIndex].description = description;
            imageList[currentIndex].photographer = photographer;
            displayCurrentImage();
            carouselMode = false;
        }, undefined);
    });
});

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return JSON.stringify({
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        });
    } else if(widget.attr('data-widget') == 'carousel') {

        if(imageList.length < 1){
            alert("Du må legge til minst ett bilde(og helst flere, hvis ikke kunne du brukt bilde-funksjonen.)");
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

function editWidget() {
    widgetBeingEdited = $(this);
    var widget = JSON.parse($(this).attr('data-json'));
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
    $("div.dialog.widget-edit[data-widget='" + widget.widget + "']").dialog('open');
}

function displayCurrentImage(){
    $("div.dialog.widget-edit[data-widget='carousel'] label[name='sequence']").text("Bilde " + (currentIndex+1) + "/" + imageList.length + " ");
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='url']").val(imageList[currentIndex].url);
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='description']").val(imageList[currentIndex].description);
    $("div.dialog.widget-edit[data-widget='carousel'] input[name='photographer']").val(imageList[currentIndex].photographer);
    
    if(imageList[currentIndex].url.trim().length < 1){
        var def = $("div.dialog.widget-edit[data-widget='carousel'] img[name='preview']").attr('default');
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
}

var currentIndex = 0;
var imageList = [];
function listImages(){
    currentIndex = 0;
    imageList = [];

    var widget = JSON.parse(widgetBeingEdited.attr('data-json'));
    var length = widget.images.length;
    imageList = widget.images;
    displayCurrentImage();
}
