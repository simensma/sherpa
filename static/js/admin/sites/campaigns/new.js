$(function() {

    var wrapper = $('div.new-campaign');
    var section_progress = wrapper.find('.section-progress');
    var chosen_image = wrapper.find('img.chosen-image');
    var chosen_image_ajaxloader = wrapper.find('img.chosen-image-ajaxloader');
    var step2 = wrapper.find('div.step2');
    var step3 = wrapper.find('div.step3');
    var crop_ratio = [940, 480];

    section_progress.find('a').click(function() {
        enableStep(Number($(this).attr('data-step')));
    });

    wrapper.find('button.pick-from-image-archive').click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            showImage(url);
            enableStep(2);
        });
    });

    wrapper.find('button.upload-new-image').click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            showImage(url);
            enableStep(2);
        });
    });

    function showImage(image_url) {
        chosen_image.off('load.image');
        chosen_image.on('load.image', function() {
            chosen_image_ajaxloader.hide();
            chosen_image.show();

            var image_ratio = chosen_image.width() / chosen_image.height();

            // Set the default selection as large as possible, but within the crop ratio
            var x2, y2;
            if(image_ratio > crop_ratio) {
                x2 = chosen_image.width();
                y2 = (chosen_image.width() / crop_ratio[0]) * crop_ratio[1];
            } else {
                x2 = (chosen_image.height() / crop_ratio[1]) * crop_ratio[0];
                y2 = chosen_image.height();
            }

            chosen_image.Jcrop({
                aspectRatio: crop_ratio[0] / crop_ratio[1],
                setSelect: [0, 0, x2, y2],
            });

        });
        chosen_image.hide();
        chosen_image_ajaxloader.show();
        chosen_image.attr('src', image_url);
    }

    function enableStep(step) {
        section_progress.find('li').removeClass('active');
        section_progress.find('li').eq(step - 1).addClass('active');
        if(step === 1) {
            wrapper.find('div.step2').hide();
            wrapper.find('div.step3').hide();
        } else if(step === 2) {
            wrapper.find('div.step2').show();
            wrapper.find('div.step3').hide();
        } else if(step === 3) {
            wrapper.find('div.step2').show();
            wrapper.find('div.step3').show();
        }
    }

});
