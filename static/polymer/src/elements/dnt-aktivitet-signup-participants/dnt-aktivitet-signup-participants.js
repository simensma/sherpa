(function () {
  Polymer({

    /* Functions */

    navigateTo: function(event, detail, sender) {
      // this.actions.goToStep('summary');
      this.state.step = 'summary';
    }

  });
})();
