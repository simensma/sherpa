(function () {
  Polymer({

    is_valid: false,
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
      this.postSignup();
    },

    postSignup: function () {
      var signupAjax = this.$.signup_ajax;
      var aktivitetDateId = parseInt(this.aktivitet_date_id, 10);
      var participantId = parseInt(this.participant.id, 10);

      var requestParams = {
        aktivitet_date: {
          id: aktivitetDateId
        },
        participants: [
          {id: participantId}
        ]
      };

      signupAjax.setAttribute('url', '/api/v2/aktivitet-signup/');
      signupAjax.body = JSON.stringify(requestParams);
      signupAjax.go();
    },

    handleSignupError: function (e) {
      this.signupError = true;
    },

    handleSignupResponse: function (event, ajax, element) {
      // TODO: If success
      this.state.step = this.steps.receipt;
    },

    validate: function () {
      this.is_valid = this.participant.is_valid;
    },


    /* Lifecycle */

    ready: function () {
      this.step.component = this;
      this.validate();
    }

  });
})();
