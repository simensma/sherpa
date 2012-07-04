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
	initialSelection = undefined;
	if(selection != undefined){
		initialSelection = selection;
	}

	var options = { 
		instance: true,
		handles: true,
		parent: parent,
		onInit: function(imag, selection){
			currentCropperImage = imag;
			setSelection(initialSelection);
		},
		onSelectChange: function(imag, selection){
			currentCropperImage = imag;
		}
	}
	
	currentCropperImageTag = img;
	currentCropperInstance = img.imgAreaSelect(options);
	if(currentCropperImage != undefined){
		currentCropperInstance.cancelSelection();
		setSelection(initialSelection);
	}	
}

function setImageCropperRatio(width, height){
	if(width != undefined && height != undefined && !isNaN(width/height) && width > 0 && height > 0){
		currentCropperInstance.setOptions({aspectRatio:(width+":"+height)});
		currentCropperInstance.update();
	}else{
		currentCropperInstance.setOptions({aspectRatio:""});
		currentCropperInstance.update();
	}
}

function setSelection(s){
	if(s != undefined){
		var cropperWidth = currentCropperImageTag.width();
		var cropperHeight = cropperWidth * (currentCropperImage.height / currentCropperImage.width);

		currentCropperInstance.setSelection(cropperWidth * s.x1, cropperHeight * s.y1, cropperWidth * s.x2, cropperHeight * s.y2);
		currentCropperInstance.setOptions({ show: true });
		currentCropperInstance.update();
	}
}