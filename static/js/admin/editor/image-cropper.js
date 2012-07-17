var currentCropperInstance;
var currentCropperImage;
var currentCropperImageTag;

//this one needs parentWidth to calculate parent Height
function addCssCropping(parentWidth, callback){
	var sel = currentCropperInstance.getSelection();
	if(sel.width <= 0 || sel.height <= 0){
		callback(undefined, undefined, undefined);
		return;
	}

	var cropperWidth = currentCropperImageTag.width();
	var cropperHeight = cropperWidth * (currentCropperImage.height / currentCropperImage.width);

	var resizeRatio = sel.height / sel.width;
	var parentHeight = parentWidth * resizeRatio;

	//zoom
	var imgWidth = cropperWidth / sel.width;
	var imgHeight = cropperHeight / sel.height;

	//margins
	var marginLeft = (sel.x1 / cropperWidth) * imgWidth;
	var marginTop = ((cropperHeight * ((sel.y1 / cropperHeight) * imgWidth)) / cropperWidth);
	var marginBot = marginTop + ((cropperHeight * (((cropperHeight - sel.y2) / cropperHeight) * imgWidth)) / cropperWidth);
	
	var cssMap = {
		"position": "relative",
		"max-width": "none",
		"width": (imgWidth*100) + "%",
		"margin-left": -(marginLeft*100) + "%",
		"margin-top": -(marginTop*100) + "%",
		"margin-bottom": -(marginBot*100) + "%"
	};

	var selection = {
		"x1":(sel.x1 / cropperWidth),
		"y1":(sel.y1 / cropperHeight),
		"x2":(sel.x2 / cropperWidth),
		"y2":(sel.y2 / cropperHeight)
	};
	//handling of data left to implementing components
	callback(cssMap, selection, Math.floor(parentHeight));
}

function closeImageCropper(){
	currentCropperInstance.cancelSelection();
	currentCropperInstance = undefined;
	currentCropperImage = undefined;
	currentCropperImageTag = undefined;
}

var initialSelection;
function openImageCropper(img, parent, selection){
	initialSelection = selection;

	var options = { 
		instance: true,
		handles: true,
		parent: parent,
		onInit: function(imag, selection){
			currentCropperImage = imag;
		},
		onSelectChange: function(imag, selection){
			currentCropperImage = imag;
		}
	}
	
	currentCropperImageTag = img;
	currentCropperInstance = img.imgAreaSelect(options);
	currentCropperInstance.cancelSelection();
	setSelection(selection);
}

function setImageCropperRatio(width, height, change){
	var cropperWidth = currentCropperImageTag.width();
	var cropperHeight = cropperWidth * (currentCropperImageTag.height() / currentCropperImageTag.width());
	
	if(width != undefined && height != undefined && !isNaN(width/height) && width > 0 && height > 0){
		currentCropperInstance.setOptions({aspectRatio:(width+":"+height)});
		if(change){
			var imgRatio = cropperWidth/cropperHeight;
			var newRatio = width/height;

			if(newRatio > imgRatio){
				currentCropperInstance.setSelection(0, 0, cropperWidth, cropperWidth*(height/width));
			}else{
				currentCropperInstance.setSelection(0, 0, cropperHeight*(width/height), cropperHeight);
			}
		}
	}else{
		currentCropperInstance.setOptions({aspectRatio:""});
		if(change){
			currentCropperInstance.setSelection(0, 0, cropperWidth, cropperHeight);
		}
	}

	currentCropperInstance.setOptions({ show: true });
	currentCropperInstance.update();
}

var insel;
function setSelection(s){
	insel = undefined;
	if(s !== undefined){
		insel = s;
		internatSetSelection();
	}
}

function internatSetSelection(){
	if(insel !== undefined){
		currentCropperInstance.cancelSelection();
		var cropperWidth = currentCropperImageTag.width();
		var cropperHeight = cropperWidth * (currentCropperImageTag.height() / currentCropperImageTag.width());
		currentCropperInstance.setSelection(cropperWidth * insel.x1, cropperHeight * insel.y1, cropperWidth * insel.x2, cropperHeight * insel.y2);
		currentCropperInstance.setOptions({ show: true });
		currentCropperInstance.update();
	}
}
