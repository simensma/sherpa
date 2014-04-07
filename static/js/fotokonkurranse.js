$(function () {

    var MAX_IMAGE_COUNT = 3;

    var fotokonkurranse = $("div.fotokonkurranse-root");
    var uploader = fotokonkurranse.find("div.uploader");
    var loader = fotokonkurranse.find("div.loader");
    var image_adder = uploader.find("div.image-adder");
    var upload_input = image_adder.find("input[type='file']");
    var images = uploader.find("div.images");
    var submit = uploader.find("button[type='submit']");
    var success_generic = uploader.find("div.upload-success-generic");

    var name = uploader.find("input[name='name']");
    var phone = uploader.find("input[name='phone']");
    var email = uploader.find("input[name='email']");

    function pendingImages() {
        // Images to send on submit
        return images.children().filter(":not(.clone):not(.upload-success):not(.sending)");
    }

    function activeImages() {
        // Either pending or already uploaded images
        return images.children().filter(":not(.clone)");
    }

    function activeImageCount() {
        return activeImages().length;
    }

    function performValidations() {
        if(!Validator.check['full_name'](name.val(), true)) {
            alert("Vær grei og fyll inn ditt fulle navn. Husk at du selv må være fotograf for bildene.");
            return false;
        }
        if(!Validator.check['phone'](phone.val(), true)) {
            alert("Fint om du kan legge inn et gyldig telefonnummer, slik at vi kan kontakte deg.");
            return false;
        }
        if(!Validator.check['email'](email.val(), true)) {
            alert("E-postadressen din er ikke gyldig! Vennligst sjekk hva du har skrevet.");
            return false;
        }
        var descriptions = true;
        pendingImages().each(function() {
            if(!Validator.check['anything']($(this).find("textarea[name='description']").val(), true)) {
                descriptions = false;
            }
        });
        if(!descriptions) {
            alert("Fint om du kan fylle ut en kort beskrivelse om sted, motiv og andre relevante opplysninger i feltet under bildet.");
            return false;
        }

        return true;
    }

    submit.click(function() {
        if(!performValidations()) {
            return $(this);
        }
        if(!confirm($(this).attr('data-confirm'))) {
            return $(this);
        }
        $(this).hide();
        name.prop('disabled', true);
        phone.prop('disabled', true);
        email.prop('disabled', true);
        pendingImages().each(function() {
            $(this).addClass('sending');
            $(this).find("textarea[name='description']").prop('disabled', true);
            $(this).find("div.cancel").hide();
            $(this).find("div.upload-success,div.upload-fail").hide();
            $(this).find("div.loader").slideDown();
            $(this).data().submit();
        });
    });

    upload_input.fileupload({
        url: uploader.attr('data-url'),
        dataType: 'json',
        autoUpload: false,
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
        maxFileSize: 20000000, // 20 MB
        disableImageResize: true,
        previewMaxWidth: 400,
        previewMaxHeight: 150,
    }).on('fileuploadadd', function(e, data) {
        if(activeImageCount() >= MAX_IMAGE_COUNT) {
            alert(images.attr('data-max-images-warning'));
            return $(this);
        }
        var file = data.files[0];
        var container = images.find("div.clone").clone().removeClass('clone').appendTo(images);
        // IE sets the placeholder value as real value in the cloned object, so remove it
        container.find("textarea[name='description']").val('');
        data.context = container;
        container.show().find("label").text(file.name);
        container.data(data);
        name.prop('disabled', false);
        phone.prop('disabled', false);
        email.prop('disabled', false);
        submit.show();
        if(activeImageCount() === MAX_IMAGE_COUNT) {
            image_adder.hide();
        }
    }).on('fileuploadprocessalways', function(e, data) {
        var file = data.files[0];
        if(file.preview) {
            data.context.find("div.preview").show().append(file.preview);
        }
        if(file.error) {
            alert(images.attr("data-canvas-error") + file.error);
            data.context.find("button.cancel").click(); // Removes this item
        }
    }).on('fileuploadsubmit', function(e, data) {
        data.formData = {
            name: name.val(),
            phone: phone.val(),
            email: email.val(),
            description: data.context.find("textarea[name='description']").val(),
        };
    }).on('fileuploadprogress', function(e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        data.context.find("div.loader .bar").css('width', progress + '%');
    }).on('fileuploaddone', function (e, data) {
        data.context.removeClass('sending').addClass('upload-success');
        var desc = data.context.find("textarea[name='description']").val();
        data.context.find("textarea[name='description']").hide();
        data.context.find("div.description").text(desc).show();
        data.context.find("div.loader").hide();
        data.context.find("div.upload-success").show();
        success_generic.slideDown();
    }).on('fileuploadfail', function (e, data) {
        data.context.removeClass('sending').addClass('upload-fail');
        data.context.find("textarea[name='description']").prop('disabled', false);
        data.context.find("div.cancel").show();
        data.context.find("div.loader").hide();
        data.context.find("div.upload-fail").show();
        name.prop('disabled', false);
        phone.prop('disabled', false);
        email.prop('disabled', false);
        submit.show();
    });

    $(document).on('click', images.selector + ' button.cancel', function() {
        $(this).parents("div.image").slideUp(function() {
            $(this).remove();
            if(activeImageCount() === 0) {
                submit.hide();
            }
        });
        image_adder.show();
    });

});
