/* Common for avanced- and article-editor */
$(document).ready(function() {

    // Hide/show chosen toolbar tab
    $("#toolbar div.tab").hide().first().show();
    $("#toolbar li").click(function() {
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

    $("#toolbar a.header").click(function() {
        document.execCommand('formatblock', false, 'h1');
    });
    $("#toolbar a.lede").click(function() {
        $(":focus").toggleClass('lede');
    });
    $("#toolbar a.body").click(function() {
        document.execCommand('formatblock', false, 'p');
    });
    $("#toolbar a.bold").click(function(event) {
        document.execCommand('bold');
    });
    $("#toolbar a.italic").click(function(event) {
        document.execCommand('italic');
    });
    $("#toolbar a.underline").click(function(event) {
        document.execCommand('underline');
    });
    $("#toolbar a.ol").click(function(event) {
        document.execCommand('insertorderedlist');
    });
    $("#toolbar a.ul").click(function(event) {
        document.execCommand('insertunorderedlist');
    });
    $("#toolbar a.anchor").click(function(event) {
        document.execCommand('createLink', false, 'TODO');
    });
    $("#toolbar a.left").click(function(event) {
        document.execCommand('justifyleft');
    });
    $("#toolbar a.center").click(function(event) {
        document.execCommand('justifycenter');
    });
    $("#toolbar a.right").click(function(event) {
        document.execCommand('justifyright');
    });
    $("#toolbar a.full").click(function(event) {
        document.execCommand('justifyfull');
    });


});
