(function () {
  Polymer({

    navigateToStep: function (event, detail, sender) {
      this.updateSteps(sender.step);
      console.log('navigateToStep', sender.step);
      window.location.hash = sender.step.slug;
    },

    updateSteps: function (newStep) {
      for (var i = 0; i < this.steps.length; i++) {
        this.steps[i].isCurrent = false;
      }

      var newStepIndex = this.steps.indexOf(newStep);
      this.steps[newStepIndex].isCurrent = true;

    },

    filterKeys: function (object) {
      return Object.keys(object);
    }

  });
})();
