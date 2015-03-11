(function () {
  Polymer({

    editParticipantDetails: function (event, detail, sender) {
      this.state.step = 'deltakere';
    },

    confirmSignup: function (event, detail, sender) {
      this.state.step = 'kvittering';
    }

  });
})();
