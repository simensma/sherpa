(function () {
  Polymer({

    /* Data model */

    aktivitet: {
        title: 'På ski i Huldreheimen',
    },
    state: {
        step: 'participants',
    },

    /* Functions */

    navigateTo: function(step) {
        this.state.step = step;
    }

  });
})();
