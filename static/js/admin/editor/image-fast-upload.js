$(document).ready(function() {

	$("div#dialog-image-fast-upload form").submit(function(e) {
		$("div#dialog-image-fast-upload div.uploading").show();
    	serializeTags();
    	$("div#dialog-image-fast-upload input[type='submit']").attr('disabled', 'disabled');
    	$("div#dialog-image-fast-upload input[type='reset']").attr('disabled', 'disabled');
	});

	$("div#dialog-image-fast-upload button.cancel-upload").click(function(e) {
    	uploadCancelled = false
    	$("div#dialog-image-fast-upload").dialog("close");
	});
});

var uploadCompleteCallback;
var uploadCancelled = false;

//the tag logic is located in admin/images/info.js
function uploadComplete(status, url){
	if(!uploadCancelled){
		if(status === "no_files"){
			$("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
			$("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
			$("div#dialog-image-fast-upload div.upload-no-files").show();
			$("div#dialog-image-fast-upload div.uploading").hide();
		} else if(status === "success"){
			var description = $("div#dialog-image-fast-upload input[name='credits']").val();
			var photographer = $("div#dialog-image-fast-upload input[name='photographer']").val();
			$("div#dialog-image-fast-upload div.uploading").hide();
			$("div#dialog-image-fast-upload").dialog("close");
			uploadCompleteCallback(url, description, photographer);
		} else {//parse error or unexpected reply
			$("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
			$("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
			$("div#dialog-image-fast-upload div.upload-failed").show();
			$("div#dialog-image-fast-upload div.uploading").hide();
		}
	}
}

function openImageUpload(callback){
	uploadCancelled = false;
	uploadCompleteCallback = callback;

	$("div#dialog-image-fast-upload").dialog("open");
	$("div#dialog-image-fast-upload input[type='submit']").removeAttr('disabled');
	$("div#dialog-image-fast-upload input[type='reset']").removeAttr('disabled');
	resetImageUpload();
}

function resetImageUpload(){
	$("div#dialog-image-fast-upload input[type='reset']").click();
	$("div#dialog-image-fast-upload input[name='tags-serialized']").val("");
	$("div#dialog-image-fast-upload div#tags").empty();

	$("div#dialog-image-fast-upload div.uploading").hide();
	$("div#dialog-image-fast-upload div.upload-failed").hide();
	$("div#dialog-image-fast-upload div.upload-no-files").hide();
}