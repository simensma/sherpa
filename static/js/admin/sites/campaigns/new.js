$(function() {

    var wrapper = $('div.new-campaign');
    var section_progress = wrapper.find('.section-progress');
    var step2 = wrapper.find('div.step2');
    var step3 = wrapper.find('div.step3');

    section_progress.find('a').click(function() {
        enableStep(Number($(this).attr('data-step')));
    });

    wrapper.find('button.pick-from-image-archive').click(function() {
        ImageArchivePicker.pick(function(url, description, photographer) {
            enableStep(2);
        });
    });

    wrapper.find('button.upload-new-image').click(function() {
        ImageUploadDialog.open(function(url, description, photographer) {
            enableStep(2);
        });
    });

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
