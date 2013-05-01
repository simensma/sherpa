/*
  Depends on ImageArchivePicker and ImageUploadDialog
 */
(function(ImageCarouselPicker, $, undefined) {

    var elements = {};
    var images = [];
    var currentIndex = 0;

    $(document).ready(function() {
        elements.picker = $("div.imagecarousel-picker");

        elements.navigation = elements.picker.find("div.navigation");
        elements.nav_current_image = elements.navigation.find("span.current");
        elements.nav_total_images = elements.navigation.find("span.total");
        elements.nav_button_prev = elements.navigation.find("button.prev");
        elements.nav_button_delete = elements.navigation.find("button.delete");
        elements.nav_button_next = elements.navigation.find("button.next");
        elements.nav_button_new = elements.navigation.find("button.new");

        elements.current_image = elements.picker.find("div.current-image");
        elements.inputs = elements.current_image.find("table.inputs");
        elements.display = elements.current_image.find("div.display");
        elements.display_image = elements.display.find("img.display");
        elements.ajaxloader = elements.display.find("img.ajaxloader");
        init();
    });

    ImageCarouselPicker.getImages = function() {
        saveCurrentImage();
        return images;
    };

    function init() {
        elements.nav_button_prev.click(function() {
            saveCurrentImage();
            currentIndex -= 1;
            resetState();
        });
        elements.nav_button_delete.click(function() {
            images = images.slice(0, currentIndex).concat(images.slice(currentIndex + 1));
            if(currentIndex + 1 > images.length && currentIndex !== 0) {
                currentIndex -= 1;
            }
            resetState();
        });
        elements.nav_button_next.click(function() {
            saveCurrentImage();
            currentIndex += 1;
            resetState();
        });
        elements.nav_button_new.click(function() {
            saveCurrentImage();
            currentIndex += 1;
            resetState();
        });
        elements.inputs.find("input[name='url']").change(function() {
            // Update the display image
            if($(this).val() === '') {
                elements.display_image.hide();
                elements.ajaxloader.hide();
            } else {
                elements.display_image.off('load.image-carousel-picker');
                elements.display_image.on('load.image-carousel-picker', function() {
                    elements.ajaxloader.hide();
                    elements.display_image.show();
                });
                elements.display_image.hide();
                elements.ajaxloader.show();
                elements.display_image.attr('src', $(this).val());
            }
        });
        elements.inputs.find("button.pick-from-image-archive").click(function() {
            ImageArchivePicker.pick(function(url, description, photographer) {
                elements.inputs.find("input[name='url']").val(url);
                elements.inputs.find("input[name='url']").change();
            });
        });
        elements.inputs.find("button.upload-new-image").click(function() {
            ImageUploadDialog.open(function(url, description, photographer) {
                elements.inputs.find("input[name='url']").val(url);
                elements.inputs.find("input[name='url']").change();
            });
        });

        if(elements.picker.is('[data-preload]')) {
            images = JSON.parse(elements.picker.attr('data-preload'));
        }

        resetState();
    }

    function saveCurrentImage() {
        var image = images[currentIndex];
        image.url = elements.inputs.find("input[name='url']").val();
        image.text = elements.inputs.find("input[name='text']").val();
        image.photographer = elements.inputs.find("input[name='photographer']").val();
    }

    function resetState() {
        // Image
        var image;
        if(currentIndex > images.length - 1) {
            // New image, create it
            image = {
                url: '',
                text: '',
                photographer: '',
                order: currentIndex
            };
            images.push(image);
        } else {
            image = images[currentIndex];
        }
        elements.inputs.find("input[name='url']").val(image.url).change();
        elements.inputs.find("input[name='text']").val(image.text);
        elements.inputs.find("input[name='photographer']").val(image.photographer);

        // Navigation
        elements.nav_current_image.text(currentIndex + 1);
        elements.nav_total_images.text(images.length);
        elements.nav_button_prev.prop('disabled', currentIndex === 0);
        if(currentIndex + 1 < images.length) {
            elements.nav_button_next.show();
            elements.nav_button_new.hide();
        } else {
            elements.nav_button_next.hide();
            elements.nav_button_new.show();
        }
    }

}(window.ImageCarouselPicker = window.ImageCarouselPicker || {}, jQuery));
