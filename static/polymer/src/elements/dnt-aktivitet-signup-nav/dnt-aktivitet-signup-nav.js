(function () {
  Polymer({

    navigateToStep: function (event, detail, sender) {
      this.updateSteps(sender.step);
      console.log('navigateToStep', sender.step);
      window.location.hash = sender.step.slug;
    },

    updateSteps: function (newStep) {
      for (var stepKey in this.steps) {
        this.steps[stepKey].isCurrent = false;
      }

      this.steps[newStep.id].isCurrent = true;

    },

    filterKeys: function (object) {
      return Object.keys(object);
    }

  });
})();
