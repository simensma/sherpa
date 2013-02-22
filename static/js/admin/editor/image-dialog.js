(function(ImageDialog, $, undefined ) {

    var imagePickedCallback; // Called when an image is picked in the dialog
    var imageRemovedCallback; // Called when an image is removed, from the dialog
    var firstOpen;
    var currentImage;

    var imageCurrentRatioWidth = 0;
    var imageCurrentRatioHeight = 0;

    $(document).ready(function() {

        var imageDialog = $("div.change-image");

        // Ensure imgareaselect follows the bootstrap-modal scrolling
        var updaterId;
        imageDialog.on('shown', function() {
            $("div.modal-scrollable").scroll(function() {
                if(updaterId !== undefined) {
                    clearTimeout(updaterId);
                }
                updaterId = setTimeout(function() {
                    if(typeof currentCropperInstance !== 'undefined') {
                        currentCropperInstance.update();
                    }
                }, 200);
            });
        });

        imageDialog.find("div#ratio-radio").append(getRatioRadioButtons());

        imageDialog.find("button.choose-image").click(function() {
            ImageArchivePicker.pick(inputDataFromSource);
        });
        imageDialog.find("button.upload-image").click(function() {
            ImageUploadDialog.open(inputDataFromSource);(inputDataFromSource);
        });

        function inputDataFromSource(url, description, photographer) {

            imageDialog.find("div.preview-container").show();

            imageDialog.find("input[name='src']").val(removeImageSizeFromUrl(url));
            imageDialog.find("input[name='description']").val(description);
            imageDialog.find("input[name='photographer']").val(photographer);
            imageDialog.find("img.preview").attr('src', addImageSizeToUrl(url, IMAGE_PPREVIEW_WIDTH));

            currentCropperInstance.cancelSelection();
            imageDialog.imagesLoaded(function() {
                openImageCropper(imageDialog.find("img.preview"), imageDialog.find("div.modal-body div.preview-container"), undefined);
                setImageRatio(true);
            });
            openImageCropper(imageDialog.find("img.preview"), imageDialog.find("div.modal-body div.preview-container"), undefined);
            setImageRatio(true);
        }

        imageDialog.find("input[name='src']").keyup(function() {
            imageDialog.find("div.preview-container").show();
            imageDialog.find("img.preview").attr('src', addImageSizeToUrl($(this).val(), IMAGE_PPREVIEW_WIDTH));
            currentCropperInstance.cancelSelection();
            setImageRatio(true);
        });

        imageDialog.find("button.insert-image").click(function() {

            var dialog = $(this).parents("div.change-image");
            var src = dialog.find("input[name='src']").val();
            if(src === "") {
                imageDialog.find("div.empty-src").show();
                return;
            }
            imageDialog.find("div.empty-src").hide();

            var parentWidth = currentImage.parent().width();

            addCssCropping(parentWidth, function(cssMap, selection, parentHeight) {
                var image = currentImage;
                var wrapper = currentImage.parent();

                var newurl = imageDialog.find("input[name='src']").val();

                if(cssMap !== undefined) {
                    src = addImageSizeToUrl(newurl, bestSizeForImage(parentWidth * (parseFloat(cssMap["width"].replace("%", ""))/100)));
                    image.css(cssMap);
                    image.attr("data-selection", JSON.stringify(selection));
                    image.attr("data-parentHeight", parentHeight);
                    wrapper.css("height", parentHeight+"px");
                } else {
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
            dialog.modal('hide');

            var anchor = dialog.find("input[name='anchor']");
            if(anchor.length > 0) {
                anchor = anchor.val().trim();
                if(anchor.length !== 0 && !anchor.match(/^https?:\/\//)) {
                    anchor = "http://" + anchor;
                }
            } else {
                anchor = '';
            }

            var description = dialog.find("input[name='description']").val();
            var photographer = dialog.find("input[name='photographer']").val();
            imagePickedCallback(src, anchor, description, photographer);
        });

        imageDialog.find("button.remove-image").click(function() {
            currentCropperInstance.cancelSelection();
            imageDialog.modal('hide');
            imageRemovedCallback();
        });

        imageDialog.find("input[name='ratio']").change(function() {
            setImageRatio(true);
        });

        imageDialog.find("div.image-details input[name='photographer']").typeahead({
            minLength: 3,
            source: function(query, process) {
                $.ajaxQueue({
                    url: '/sherpa/bildearkiv/fotograf/',
                    data: { name: query }
                }).done(function(result) {
                    process(JSON.parse(result));
                });
            }
        });
    });

    ImageDialog.openImageDialog = function(opts) {
        firstOpen = false;
        currentImage = opts.image;
        imagePickedCallback = opts.save;
        imageRemovedCallback = opts.remove;

        var src = removeImageSizeFromUrl(opts.image.attr("src"));

        var dialog = $("div.change-image");
        dialog.find("div.image-details").show();
        dialog.find("div.empty-src").hide();
        dialog.find("img.preview").attr('src', addImageSizeToUrl(src, IMAGE_PPREVIEW_WIDTH));
        dialog.modal();

        dialog.find("input[name='src']").val(src);
        if(opts.anchor !== undefined) {
            dialog.find("input[name='anchor']").val(opts.anchor);
            dialog.find("tr.anchor").show();
        } else {
            dialog.find("tr.anchor").hide();
        }
        if(opts.description !== undefined) {
            dialog.find("input[name='description']").val(opts.description);
            dialog.find("tr.description").show();
        } else {
            dialog.find("tr.description").hide();
        }
        if(opts.photographer !== undefined) {
            dialog.find("input[name='photographer']").val(opts.photographer);
            dialog.find("tr.photographer").show();
        } else {
            dialog.find("tr.photographer").hide();
        }

        var sel = opts.image.attr("data-selection");
        if(sel === undefined || sel === "") {
            sel = undefined;
        } else {
            sel = JSON.parse(sel);
        }

        var ratioW = opts.image.attr("data-ratio-width");
        var ratioH = opts.image.attr("data-ratio-height");
        if(ratioIsValid(ratioW, ratioH)) {
            //select correct ratiio-radio
            var chosenRatio = ratioW + ":" + ratioH;
            dialog.find("input[name='ratio']").each(function() {
                if($(this).val() == chosenRatio) {
                    $(this).prop("checked", true);
                }
            });
        } else {
            dialog.find("input[name='ratio'][value='" + DEFAULT_CROP_RATIO +"']").prop("checked", true);
        }

        dialog.imagesLoaded(function() {
            openImageCropper(dialog.find("img.preview"), dialog.find("div.modal-body div.preview-container"), sel);
            setImageRatio((sel === undefined));
            if(src.trim().length < 1) {
                dialog.find("div.preview-container").hide();
                currentCropperInstance.cancelSelection();
            }
        });

        //hax for preventing saving of empty image and crash of database as result
        if(src.trim().length < 1) {
            firstOpen = true;
            imagePickedCallback("http://www.turistforeningen.no/static/img/placeholder.png", "", "", "");
        }
    };

    function setImageRatio(change) {
        try {
            var checked = $("div.change-image input[name='ratio']:checked").val().split(":");
            imageCurrentRatioWidth = parseInt(checked[0]);
            imageCurrentRatioHeight = parseInt(checked[1]);
        } catch(e) {
            imageCurrentRatioWidth = 0;
            imageCurrentRatioHeight = 0;
        }

        if(ratioIsValid(imageCurrentRatioWidth, imageCurrentRatioHeight)) {
            setImageCropperRatio(imageCurrentRatioWidth, imageCurrentRatioHeight, change);
        } else {
            setImageCropperRatio(0, 0, change);
        }
    }

}(window.ImageDialog = window.ImageDialog || {}, jQuery ));
