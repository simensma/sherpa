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

    // add another pictureline to carousell
    $("div.dialog.widget-edit button.add-image").click(function() {
        listImages(true);
    });
});

function getImagesFromCarouselEdit(widget){
    var rows = widget.find("table[name='imagetable'] tbody").children();

    var list = [];
    for(var i = 0; i < rows.length; i++){
        var url = $(rows[i].cells).find("input[name^='url']").val();
        i++;
        var description = $(rows[i].cells).find("input[name^='description']").val();
        i++;
        var photographer = $(rows[i].cells).find("input[name^='photographer']").val();

        if(url.trim().length > 1){
            list.push({
                url: url,
                description: description,
                photographer: photographer
            });
        }
    }
    return list;
}

function validateContent(widget) {
    if(widget.attr('data-widget') == 'quote') {
        return JSON.stringify({
            widget: "quote",
            quote: widget.find("textarea[name='quote']").val(),
            author: widget.find("input[name='author']").val()
        });
    } else if(widget.attr('data-widget') == 'carousel') {

        var list = getImagesFromCarouselEdit(widget);
        if(list.length < 1){
            alert("Du må legge til minst ett bilde(og helst flere, hvis ikke kunne du brukt bilde-funksjonen.)");
            return false;
        }

        return JSON.stringify({
            widget: "carousel",
            images: list
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
        listImages(false);
    }
    $("div.dialog.widget-edit[data-widget='" + widget.widget + "']").dialog('open');
}


var imageList = [];
function listImages(add){
    var widget = JSON.parse(widgetBeingEdited.attr('data-json'));
    var length = widget.images.length;

    var images = widget.images;
    var descriptions = widget.descriptions

    if(add == true){
        images = getImagesFromCarouselEdit($("div.dialog.widget-edit[data-widget='carousel']"));
        length = images.length + 1;
    }

    $("div.dialog.widget-edit[data-widget='carousel'] table[name='imagetable'] tr").remove();
    for(var i = 0; i < length; i++){
        var url;
        var description;
        var photographer;
        if(i == images.length){
            url = "";
            description = "";
            photographer = "";
        }else{
            url = images[i].url;
            description = images[i].description;
            photographer = images[i].photographer;
        }
        $("div.dialog.widget-edit[data-widget='carousel'] table[name='imagetable']").append(
            "<tr name='"+ i +"'>" + 
                "<td><label>Url:</label></td>" +
                "<td><input name='url"+ i +"' type='text' class='input-xlarge' value='" + url + "'></td>" +
                "<td><button name='choose"+ i +"'' class='btn btn-success choose-image'><i class='icon-share-alt'></i> Finn bilde i arkivet</button></td>" +
                "<td><button name='remove"+ i +"' class='btn btn-danger remove-image'><i class='icon-remove'></i> Fjern bilde</button></td>" +
            "</tr>" + 
            "<tr name='descriptionrow"+ i +"'>" + 
                "<td><label>Beskrivelse:</label></td>" +
                "<td><input name='description"+ i +"' type='text' class='input-xlarge' value='" + description + "'></td>" +
            "</tr>" +
            "<tr name='photographerrow"+ i +"'>" + 
                "<td><label>Fotograf:</label></td>"+
                "<td><input name='photographer"+ i +"' type='text' class='input-xlarge' value='" + photographer + "'></td>" +
            "</tr>"
        );

        //remove clicked
        $("div.dialog.widget-edit[data-widget='carousel'] button[name='remove"+ i +"']").click(function(){
            var name = $(this).attr('name');
            var index = name.charAt(name.length -1);
            $("div.dialog.widget-edit[data-widget='carousel'] table[name='imagetable'] tr[name='"+ index +"']").remove();
            $("div.dialog.widget-edit[data-widget='carousel'] table[name='imagetable'] tr[name='descriptionrow"+ index +"']").remove();
            $("div.dialog.widget-edit[data-widget='carousel'] table[name='imagetable'] tr[name='photographerrow"+ index +"']").remove();
            widget.images = getImagesFromCarouselEdit($("div.dialog.widget-edit[data-widget='carousel']"));
            widgetBeingEdited.attr('data-json', JSON.stringify(widget));
        });

        //choose clicked
        $("div.dialog.widget-edit[data-widget='carousel'] button[name='choose"+ i +"']").click(function(){
            carouselMode = true;
            var name = $(this).attr('name');
            var index = name.charAt(name.length -1);

            openImageDialog(undefined, undefined, undefined, undefined, function(src){
                $("div.dialog.widget-edit[data-widget='carousel'] input[name='url"+ index +"']").val(src);
                carouselMode = false;
            }, undefined);
            $("div#dialog-change-image div.image-details").hide();
            $("div#dialog-change-image div.image-archive-chooser").show();

        });
    }
}
