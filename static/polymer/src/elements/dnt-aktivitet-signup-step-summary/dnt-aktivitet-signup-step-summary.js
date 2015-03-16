(function () {
  Polymer({

    terms_and_conditions_accepted: false,

    observe: {
      'terms_and_conditions_accepted': 'termsAndConditionsAcceptedChanged'
    },

    termsAndConditionsAcceptedChanged: function () {
    },

    editParticipantDetails: function (event, detail, sender) {
      this.state.step = 'deltakere';
    },

    confirmSignup: function (event, detail, sender) {
      this.state.step.hasPassed = true;
      this.state.step = 'kvittering';
    }

  });
})();
