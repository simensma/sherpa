(function () {
  Polymer({

    is_valid: false,


    /* Observers */

    observe: {
      '$.participant.is_valid': 'participantIsValidChanged'
    },

    participantIsValidChanged: function (oldVal, newVal) {
      this.validate();
    },


    /* Functions */

    validate: function () {
      var participantIsValid = (!!this.$.participant) ? this.$.participant.is_valid : false;
      if (participantIsValid !== undefined) {
        this.is_valid = participantIsValid;
      }
    },

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
      this.validate();
    }

  });
})();
