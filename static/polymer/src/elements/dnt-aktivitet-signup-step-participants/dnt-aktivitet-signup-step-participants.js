(function () {
  Polymer({

    /* Functions */

    navigateTo: function (event, detail, sender) {
      this.state.step.hasPassed = true;
      this.state.step = 'oppsummering';
    }

  });
})();
