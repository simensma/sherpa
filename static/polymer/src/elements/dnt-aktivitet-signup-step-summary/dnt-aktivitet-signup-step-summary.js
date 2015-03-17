(function () {
  Polymer({

    isValid: false,
    terms_and_conditions_accepted: false,

    /* Observers */

    observe: {
      'terms_and_conditions_accepted': 'termsAndConditionsAcceptedChanged'
    },

    termsAndConditionsAcceptedChanged: function () {
    },


    /* Functions */

    editParticipantDetails: function (event, detail, sender) {
      this.state.step = this.steps.participants;
    },

    confirmSignup: function (event, detail, sender) {
      this.state.step.isAvailable = true;
      this.state.step = this.steps.receipt;
    },

    validate: function () {
      this.isValid = true;
    },


    /* Lifecycle */

    ready: function () {
      this.step.component = this;
      this.validate();
    }

  });
})();
