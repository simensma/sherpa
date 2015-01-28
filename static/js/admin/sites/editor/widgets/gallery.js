(function(ImageGalleryWidgetEditor, $, undefined ) {

    /* Private variables */

    var image_list = [];
    var $widget_editor; // Will be set in the document.ready block further down
    var $widget_being_edited; // Used when editing existing widget
    var gallery_layout = 'carousel'; // Alternative is album

    var $empty_section = $('.section.section-empty');
    var $images_section = $('.section.section-images');
    var $settings_section = $('.section.section-settings');
    var $meta_editor; // Will be set in the document.ready block further down
    var $image_list_container = $('[data-dnt-container="image-list"]');


    /* Private methods */

    function chooseFromSource (images) {
        if (typeof images === 'object') {
            for (var i = 0; i < images.length; i++) {
                var image = images[i];
                addImage({
                    url: image.url,
                    selection: undefined,
                    description: image.description,
                    photographer: image.photographer
                });
            }
        }
    }

    function getFromUpload (url, description, photographer) {
        addImage({
            url: url,
            selection: undefined,
            description: description,
            photographer: photographer
        });
    }

    function addImage (image) {

        if ($empty_section.is(':visible')) {
            $empty_section.hide();
            $images_section.show();
            $settings_section.show();
        }

        var $new_image_container = $('[data-dnt-container="insertion-templates"] .gallery-editor-image.image').clone();
        $new_image_container.find('img').attr('src', image.url);

        setImageMetaData($new_image_container.find('img'), image);

        $new_image_container.appendTo($image_list_container);
        $image_list_container.sortable('refresh');
    }

    function getImageMetaData ($image) {
        var imageMetaData = {
            url: $image.attr('data-dnt-url'),
            description: $image.attr('data-dnt-description'),
            photographer: $image.attr('data-dnt-photographer')
        };

        return imageMetaData;
    }

    function setImageMetaData ($image, imageMetaData) {
        if (!!imageMetaData.url) {
            $image.attr('data-dnt-url', imageMetaData.url);
        }
        if (!!imageMetaData.description) {
            $image.attr('data-dnt-description', imageMetaData.description);
        }
        if (!!imageMetaData.photographer) {
            $image.attr('data-dnt-photographer', imageMetaData.photographer);
        }
    }

    function setMetaEditorImage ($image) {
        var $description_field = $meta_editor.find('input[name="description"]');
        var $photographer_field = $meta_editor.find('input[name="photographer"]');
        var $image_preview = $meta_editor.find('.preview img');

        var image_data = getImageMetaData($image);
        $meta_editor.data('$image', $image);

        $image_preview.attr('src', image_data.url);
        $description_field.val(image_data.description);
        $photographer_field.val(image_data.photographer);
    }


    /* Public methods */

    ImageGalleryWidgetEditor.init = function () {
        $image_list_container.empty();
        $meta_editor.hide();
        $empty_section.hide();
        $images_section.hide();
        $settings_section.hide();

        // Init sortable behavior of images container
        // No need to wait for images, as it will be refreshed for each image added
        $image_list_container.sortable({
            items: '.image',
            cursor: 'move'
        });

        // Add the imageset images to the editor if any
        ImageGalleryWidgetEditor.listImages();

        // Show the correct layout group button as the active one
        $widget_editor.find('[data-dnt-name="layout"][data-dnt-value="' + gallery_layout + '"]').addClass('active');

        // Open modal
        $widget_editor.modal();
    };

    ImageGalleryWidgetEditor.listImages = function () {

        if (typeof $widget_being_edited === 'undefined') {
            $empty_section.show();

        } else {
            $images_section.show();
            $settings_section.show();

            var widget = JSON.parse($widget_being_edited.attr('data-json'));

            for (var i = 0; i < widget.images.length; i++) {
                addImage(widget.images[i]);
            }
        }
    };


    /* New widget */

    $(document).on('widget.new.gallery', function (e, editor_callback) {
        WidgetEditor.setCallback(editor_callback);
        $widget_being_edited = undefined;
        ImageGalleryWidgetEditor.init();
    });


    /* Edit widget */

    $(document).on('widget.edit', 'div.widget.gallery', function (e, widget_content, editor_callback) {
        WidgetEditor.setCallback(editor_callback);
        $widget_being_edited = $(this);
        gallery_layout = widget_content.layout || gallery_layout;
        ImageGalleryWidgetEditor.init();
    });


    /* On document load */

    $(function () {

        $widget_editor = $('div.widget-editor[data-widget="gallery"]');
        $meta_editor = $widget_editor.find('.image-meta-editor');

        $(document).on('click', $image_list_container.find('.image a').selector, function (e) {
            $image_list_container.find('.image a').removeClass('active');
            $(this).addClass('active');
            $image = $(this).find('img');
            setMetaEditorImage($image);
            $meta_editor.show();
        });

        // Enable Bootstrap Well dismissal
        $(document).on('click', $widget_editor.find('[data-dismiss="well"]').selector, function (e) {
            $image_list_container.find('.image a').removeClass('active');
            $(this).parents('.well').first().hide();
        });

        // Stop Carousel spinning
        $('.carousel').each(function(){
            $(this).carousel({
                interval: false
            });
        });

        // Remove image from carousel
        $(document).on('click', $widget_editor.find('[data-dnt-trigger="remove-image"]').selector, function (e) {
            e.stopPropagation(); // Prevent sending click event to image as that will trigger metadata editor
            var $image_to_remove = $(this).parents('.image').first();
            var image_to_remove_url = $image_to_remove.find('img').first().attr('src');

            if ($meta_editor.data('$image') && ($meta_editor.data('$image').attr('src') === image_to_remove_url)) {
                $meta_editor.hide();
            }

            $image_to_remove.remove();
            $image_list_container.sortable('refresh');
        });

        // Change default layout
        $(document).on('click', $widget_editor.find('[data-dnt-name="layout"]').selector, function (e) {
            $(this).siblings().removeClass('active');
            $(this).addClass('active');
            gallery_layout = $(this).attr('data-dnt-value');
        });

        // Clicked add images button
        $widget_editor.find('[data-dnt-trigger="open-add-images-dialog"]').click(function () {
            ImageArchivePicker.pick(chooseFromSource, {multiselect: true});
        });

        // Clicked upload image button
        $widget_editor.find('[data-dnt-trigger="open-upload-image-dialog"]').click(function () {
            ImageUploadDialog.open(getFromUpload);
        });

        // Update image metadata on input

        $widget_editor.find("input[name='description']").on('input', function () {
            var $image = $meta_editor.data('$image');
            $image.attr('data-dnt-description', $(this).val().trim());
        });

        $widget_editor.find("input[name='photographer']").on('input', function () {
            var $image = $meta_editor.data('$image');
            $image.attr('data-dnt-photographer', $(this).val().trim());
        });

        /* Saving */

        $widget_editor.find('button.save').click(function() {
            var image_list = [];

            var $images = $image_list_container.find('.image img');

            $images.each(function (index, img) {
                image_list.push(getImageMetaData($(img)));
            });

            if (image_list.length < 1) {
                alert('Du må legge til minst ett bilde (og helst flere, hvis ikke kunne du brukt bildeelementet)');
                return $(this);
            }

            WidgetEditor.saveWidget({
                widget: 'gallery',
                images: image_list,
                layout: gallery_layout
            });
            $widget_editor.modal('hide');
        });

    });

}(window.ImageGalleryWidgetEditor = window.ImageGalleryWidgetEditor || {}, jQuery ));
