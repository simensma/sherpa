var imagePickedCallback; // Called when an image is picked in the dialog
var imageRemovedCallback; // Called when an image is removed, from the dialog
var currentImage;
var cancelRequested 

$(document).ready(function() {

    $("div#dialog-change-image").parent().find("a.ui-dialog-titlebar-close").click(function() {
        if(currentImage.attr("src").trim().length < 1){
            currentCropperInstance.cancelSelection();
            imageRemovedCallback();
        }
    });

    $("div#dialog-change-image button.choose-image").click(function() {
        chooseImagefromArchive(function(url, description, photographer){
            $("div#dialog-change-image input[name='src']").val(url);
            $("div#dialog-change-image input[name='description']").val(description);
            $("div#dialog-change-image input[name='photographer']").val(photographer);
            $("div#dialog-change-image img.preview").attr('src', url);

            currentCropperInstance.cancelSelection();
            openImageCropper($("div#dialog-change-image img.preview"), $("div#dialog-change-image"), undefined);
        });
    });

    $("div#dialog-change-image input[name='src']").keyup(function() {
        $("div#dialog-change-image img.preview").attr('src', '/static/img/ajax-loader-small.gif');
        $("div#dialog-change-image img.preview").attr('src', $(this).val());
    });

    $("div#dialog-change-image button.insert-image").click(function() {

        addCssCropping(currentImage.parent().width(), function(cssMap, selection, parentHeight){
            var image = currentImage;
            var wrapper = currentImage.parent();

            if(cssMap != undefined){
                image.css(cssMap);
                image.attr("data-selection", JSON.stringify(selection));
                image.attr("data-parentHeight", parentHeight);
                wrapper.css("height", parentHeight+"px");
            }else{
                image.removeAttr("style");
                image.removeAttr("data-selection");
                image.removeAttr("data-parentHeight");
                image.css("width", "100%");
                wrapper.css("height", "auto");
            }
        });
        currentCropperInstance.cancelSelection();

        var dialog = $(this).parents("div#dialog-change-image");
        var src = dialog.find("input[name='src']").val();
        if(src == "") {
            $("div#dialog-change-image div.empty-src").show();
            return;
        }
        $("div#dialog-change-image div.empty-src").hide();
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
});

function openImageDialog(image, anchor, description, photographer, saveCallback, removeCallback) {
    currentImage = image;

    var src = image.attr("src");

    $("div#dialog-change-image div.image-details").show();
    $("div#dialog-change-image div.empty-src").hide();
    $("div#dialog-change-image img.preview").attr('src', src);

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
        dialog.find("tr.description").show();
    } else {
        dialog.find("tr.description").hide();
    }
    if(photographer !== undefined) {
        dialog.find("input[name='photographer']").val(photographer);
        dialog.find("tr.photographer").show();
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

    openImageCropper($("div#dialog-change-image img.preview"), dialog, sel);
    imagePickedCallback = saveCallback;
    imageRemovedCallback = removeCallback;
}