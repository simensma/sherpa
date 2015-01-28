$(function() {

    var default_gallery_layout = 'carousel'; // Alternative is album

    var $empty_section;
    var $images_section;
    var $settings_section;
    var $meta_editor;
    var $image_list_container;

    WidgetEditor.listen({
        widget_name: 'gallery',

        init: function($editor) {

            /* Lookup and assign editor-local element variables */

            $empty_section = $editor.find('.section.section-empty');
            $images_section = $editor.find('.section.section-images');
            $settings_section = $editor.find('.section.section-settings');
            $meta_editor = $editor.find('.image-meta-editor');
            $image_list_container = $editor.find('[data-dnt-container="image-list"]');

            // Init sortable behavior of images container
            // No need to wait for images, as it will be refreshed for each image added
            $image_list_container.sortable({
                items: '.image',
                cursor: 'move',
            });

            /* Declare event listeners */

            $(document).on('click', $image_list_container.find('.image a').selector, function (e) {
                $image_list_container.find('.image a').removeClass('active');
                $(this).addClass('active');
                $image = $(this).find('img');
                setMetaEditorImage($image);
                $meta_editor.show();
            });

            // Enable Bootstrap Well dismissal
            $(document).on('click', $editor.find('[data-dismiss="well"]').selector, function (e) {
                $image_list_container.find('.image a').removeClass('active');
                $(this).parents('.well').first().hide();
            });

            // Remove image from carousel
            $(document).on('click', $editor.find('[data-dnt-trigger="remove-image"]').selector, function (e) {
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
            $editor.find('[data-dnt-name="layout"]').click(function(e) {
                $(this).siblings().removeClass('active');
                $(this).addClass('active');
            });

            // Clicked add images button
            $editor.find('[data-dnt-trigger="open-add-images-dialog"]').click(function () {
                ImageArchivePicker.pick(function(images) {
                    for (var i = 0; i < images.length; i++) {
                        addImage(images[i]);
                    }
                }, {multiselect: true});
            });

            // Clicked upload image button
            $editor.find('[data-dnt-trigger="open-upload-image-dialog"]').click(function () {
                ImageUploadDialog.open(addImage);
            });

            // Update image metadata on input

            $editor.find("input[name='description']").on('input', function () {
                var $image = $meta_editor.data('$image');
                $image.attr('data-dnt-description', $(this).val().trim());
            });

            $editor.find("input[name='photographer']").on('input', function () {
                var $image = $meta_editor.data('$image');
                $image.attr('data-dnt-photographer', $(this).val().trim());
            });

        },

        onNew: function($editor) {
            resetEditor();

            // Show the correct layout group button as the active one
            $editor.find('[data-dnt-name="layout"][data-dnt-value="' + default_gallery_layout + '"]').addClass('active');

            $empty_section.show();
        },

        onEdit: function($editor, widget_content) {
            resetEditor();

            // Show the correct layout group button as the active one
            $editor
                .find('[data-dnt-name="layout"][data-dnt-value="' + widget_content.layout + '"]')
                .addClass('active');

            // Add the imageset images to the editor if any
            $images_section.show();
            $settings_section.show();

            for (var i = 0; i < widget_content.images.length; i++) {
                addImage(widget_content.images[i]);
            }

        },

        onSave: function($editor) {
            var image_list = [];

            var $images = $image_list_container.find('.image img');

            $images.each(function (index, img) {
                image_list.push(getImageMetaData($(img)));
            });

            if (image_list.length < 1) {
                alert('Du må legge til minst ett bilde (og helst flere, hvis ikke kunne du brukt bildeelementet)');
                return false;
            }

            WidgetEditor.saveWidget({
                widget: 'gallery',
                images: image_list,
                layout: $editor.find('[data-dnt-name="layout"].active').attr('data-dnt-value'),
            });
            return true;
        }
    });

    function resetEditor($editor) {
        $image_list_container.empty();
        $meta_editor.hide();
        $empty_section.hide();
        $images_section.hide();
        $settings_section.hide();
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

});
