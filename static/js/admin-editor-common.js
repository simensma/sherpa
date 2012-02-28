/* Common for avanced- and article-editor */
$(document).ready(function() {

    // Hide/show chosen toolbar tab
    $("#toolbar div.tab").hide().first().show();
    $("#toolbar li").click(function() {
        $("#toolbar li").removeClass('active');
        $(this).addClass('active');
        $("#toolbar div.tab").hide();
        $($("#toolbar div.tab")[$(this).index()]).show();
    });
    // Make toolbar draggable
    $("#toolbar").draggable({
        containment: 'window'
    });
    // Draggable will set position relative, so make sure it is fixed before the user drags it
    $("#toolbar").css('position', 'fixed');

    /* Toolbar buttons */

    $("#toolbar div.button").mousedown(function() {
        $(this).toggleClass('active');
    }).mouseup(function() {
        $(this).toggleClass('active');
    });

    $("#toolbar div.button.header").click(function() {
        document.execCommand('formatblock', false, 'h1');
    });
    $("#toolbar div.button.lede").click(function() {
        $(":focus").toggleClass('lede');
    });
    $("#toolbar div.button.body").click(function() {
        document.execCommand('formatblock', false, 'p');
    });
    $("#toolbar div.button.bold").click(function(event) {
        document.execCommand('bold');
    });
    $("#toolbar div.button.italic").click(function(event) {
        document.execCommand('italic');
    });
    $("#toolbar div.button.underline").click(function(event) {
        document.execCommand('underline');
    });
    $("#toolbar div.button.ol").click(function(event) {
        document.execCommand('insertorderedlist');
    });
    $("#toolbar div.button.ul").click(function(event) {
        document.execCommand('insertunorderedlist');
    });
    $("#toolbar div.button.anchor").click(function(event) {
        document.execCommand('createLink', false, 'TODO');
    });
    $("#toolbar div.button.left").click(function(event) {
        document.execCommand('justifyleft');
    });
    $("#toolbar div.button.center").click(function(event) {
        document.execCommand('justifycenter');
    });
    $("#toolbar div.button.right").click(function(event) {
        document.execCommand('justifyright');
    });
    $("#toolbar div.button.full").click(function(event) {
        document.execCommand('justifyfull');
    });


});
