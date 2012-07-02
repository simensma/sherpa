var currentCropperInstance;
var currentCropperImage;
var currentCropperImageTag;

function addCssCropping(image, wrapper){
	var sel = currentCropperInstance.getSelection();
	if(sel.width <= 0 || sel.height <= 0){
		wrapper.css("height", "auto");
		image.removeAttr("style");
		image.removeAttr("selection");
		image.removeAttr("parentHeight");
		return;
	}

	var cropperWidth = currentCropperImageTag.width();
	var cropperHeight = cropperWidth * (currentCropperImage.height / currentCropperImage.width);

	var resizeRatio = sel.height / sel.width;

	var parentWidth = wrapper.width();
	var parentHeight = wrapper.width() * resizeRatio;
	wrapper.css("height", Math.floor(parentHeight) + "px");
	//stored in the image for use on first render
	image.attr("parentHeight", Math.floor(parentHeight));

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
	image.css(cssMap);

	var selection = JSON.stringify({
		"x1":(sel.x1 / cropperWidth),
		"y1":(sel.y1 / cropperHeight),
		"x2":(sel.x2 / cropperWidth),
		"y2":(sel.y2 / cropperHeight)
	});
	image.attr("selection", selection);
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
		initialSelection = JSON.parse(selection);
	}

	currentCropperImageTag = img;
	currentCropperInstance = img.imgAreaSelect({ 
		instance: true,
		handles: true,
		parent: parent,
		onInit: function(imag, selection){
			currentCropperImage = imag;
			setSelection(initialSelection)
		},
		onSelectChange: function(imag, selection){
			currentCropperImage = imag;
		}
	});
	if(currentCropperImage != undefined){
		currentCropperInstance.cancelSelection();
		setSelection(initialSelection);
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