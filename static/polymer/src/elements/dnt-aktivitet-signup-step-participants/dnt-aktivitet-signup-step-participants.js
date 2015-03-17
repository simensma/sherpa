(function () {
  Polymer({

    is_valid: false,


    /* Observers */

    observe: {},

    validate: function () {
      this.is_valid = true;
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
