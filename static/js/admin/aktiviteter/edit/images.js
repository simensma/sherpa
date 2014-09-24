$(function() {
    var scope = $('.section.images');

    $.fn.reIndexInputNames = function() {
        $(this).each(function(i) {
            $(this).find('[name^="images"]').each(function() {
                var name = $(this).attr('name').replace(/\[[\w]+\]/, '[' + i + ']');
                $(this).attr('name', name);
            });
        });
    };

    function imageAddHandler(url, description, photographer) {
        // Remove any alerts before adding the new image
        scope.find('[data-dnt-container="images"] > .alert').remove();

        var i = scope.find('[data-dnt-container="images"]').children().length;
        var image = scope.find('[data-dnt-template="image"] > div').clone(true, true);

        image.find('.thumbnail img').attr('src', url);
        image.find('[name="images[tmp][url]"]').val(url);
        image.find('[name="images[tmp][description]"]').val(description);
        image.find('[name="images[tmp][photographer]"]').val(photographer);

        scope.find('[data-dnt-container="images"]').append(image);
        scope.find('[data-dnt-container="images"] > div').reIndexInputNames();
    }

    scope.find('[data-dnt-action="image-remove"]').click(function(e) {
        e.preventDefault();
        $(this).parents('.aktivitet-image').remove();
        scope.find('[data-dnt-container="images"] > div').reIndexInputNames();
    });

    scope.find('[data-dnt-action="image-select"]').click(function() {
        ImageArchivePicker.pick(imageAddHandler);
    });

    scope.find('[data-dnt-action="image-upload"]').click(function() {
        ImageUploadDialog.open(imageAddHandler);
    });
});

