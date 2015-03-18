(function () {
  Polymer({

    is_valid: false,


    /* Observers */

    observe: {
      'participant.is_valid': 'participantIsValidChanged'
    },

    participantIsValidChanged: function () {
      // If participant is invalid, the step is invalid
      this.is_valid = this.participant.is_valid;
    },

    validate: function () {
      this.is_valid = this.participant.is_valid;
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
