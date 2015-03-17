(function () {
  Polymer({

    isValid: false,


    /* Observers */

    observe: {},

    validate: function () {
      this.isValid = true;
    },


    /* Functions */

    goToPrevStep: function (event, detail, sender) {
      this.state.step = this.steps.description;
    },

    goToNextStep: function (event, detail, sender) {
      this.state.step = this.steps.summary;
    },


    /* Lifecycle */

    ready: function () {
      this.step.isAvailable = true;
      this.step.component = this;
      this.validate();
    }

  });
})();
