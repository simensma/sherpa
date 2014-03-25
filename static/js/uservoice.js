//
// UserVoice Javascript SDK developer documentation:
// https://www.uservoice.com/o/javascript-sdk
//

(function() {
    var uv=document.createElement('script');
    uv.type='text/javascript';
    uv.async=true;
    uv.src='//widget.uservoice.com/sjQEGc2xV1ahxZg1IlQbQQ.js';
    var s=document.getElementsByTagName('script')[0];s.parentNode.insertBefore(uv,s);
})();

UserVoice = window.UserVoice || [];
UserVoice.push(['showTab', 'classic_widget', {
    mode: 'full',
    primary_color: '#0072b4',
    link_color: '#d82c20',
    default_mode: 'support',
    forum_id: 235824,
    tab_label: 'Spørsmål eller tilbakemeldinger?',
    tab_color: '#d83020',
    tab_position: 'middle-right',
    tab_inverted: false
}]);

// Identify the user and pass traits
UserVoice.push(['identify', window.User]);
