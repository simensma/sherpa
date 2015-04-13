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
      this.steps.summary.isAvailable = true;
    },


    /* Lifecycle */

    ready: function () {

      // Add event listener because textarea can not be added to observe object like other inputs
      this.$.comment_input.addEventListener('input', $.proxy(function (e) {
        var comment = e.target.value;
        this.comment = comment;
      }, this));

      this.step.isAvailable = true;
      this.step.component = this;
      this.validate();
    }

  });
})();
