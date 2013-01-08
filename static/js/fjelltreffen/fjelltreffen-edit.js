$(document).ready(function() {
    
    

    var annonseid = $("div.annonse").attr("data-id");
    var hidden = $("div.annonse").attr("data-hidden");

    $("button.save-annonse").click(function(){
        disableButtons();
        saveAnnonse(hidden);
    });
    $("button.publish-annonse").click(function(){
        disableButtons();
        saveAnnonse(false);
    });
    $("button.hide-annonse").click(function(){
        disableButtons();
        saveAnnonse(true);
    });
    $("button.delete-annonse").click(function(){
        disableButtons();
        deleteAnnonse();
    });

    function deleteAnnonse(){
        $.ajaxQueue({
            url: '/fjelltreffen/delete/' + annonseid + "/",
        }).done(function(result) {
            console.log("done")
        }).fail(function(result) {
            console.log("fail")
            enableButtons();
        }).always(function() {
            
        });
    }

    function saveAnnonse(hide){
        content = {
            id:annonseid,
            hidden:hide,
            hideage:$("input.annonse-hideage").prop("checked"),
            title:$("input.annonse-title").val(),
            text:$("textarea.annonse-text").val(),
            fylke:$("select.annonse-fylke").val()
        }
        console.log(content);
        $.ajaxQueue({
            url: '/fjelltreffen/save/',
            data: 'annonse=' + JSON.stringify(content)
        }).done(function(result) {
            returnedData = JSON.parse(result);
            hidden = returnedData['hidden'];
            annonseid = returnedData['id']
            console.log(returnedData)
        }).fail(function(result) {
            console.log("fail");
        }).always(function() {
            enableButtons();
        });

    }

    function disableButtons(){
        $("button.save-annonse").attr("disabled", true)
        $("button.publish-annonse").attr("disabled", true)
        $("button.hide-annonse").attr("disabled", true)
        $("button.delete-annonse").attr("disabled", true)
    }

    function enableButtons(){
        $("button.save-annonse").attr("disabled", false)
        if(hidden){
            $("button.publish-annonse").attr("disabled", false)
            $("button.publish-annonse").show()
            $("button.hide-annonse").attr("disabled", true)
            $("button.hide-annonse").hide()
        }else{
            $("button.publish-annonse").attr("disabled", true)
            $("button.publish-annonse").hide()
            $("button.hide-annonse").attr("disabled", false)
            $("button.hide-annonse").show()
        }
        $("button.delete-annonse").attr("disabled", false)
        $("button.delete-annonse").show()
    }
});