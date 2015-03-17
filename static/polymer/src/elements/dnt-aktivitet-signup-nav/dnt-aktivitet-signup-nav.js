(function () {
  Polymer({

    navigateToStep: function (event, detail, sender) {
      if (!sender.hasAttribute('disabled')) {
        this.state.step = this.steps[sender.step.id];
      }
    },

    filterKeys: function (object) {
      return Object.keys(object);
    }

  });
})();
