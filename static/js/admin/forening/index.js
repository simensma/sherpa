$(function() {
    var foreningsadmin = $("div.foreningsadmin");

    var metadata = foreningsadmin.find("ul.nav li a[href='#metadata']");
    var grupper = foreningsadmin.find("ul.nav li a[href='#grupper']");
    var brukere = foreningsadmin.find("ul.nav li a[href='#brukere']");

    $.fn.Hashtag({
        'metadata': { 'match': function(id) { metadata.tab('show'); }},
        'grupper': { 'match': function(id) { grupper.tab('show'); }},
        'brukere': { 'match': function(id) { brukere.tab('show'); }},
    });

});
