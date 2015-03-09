(function () {
  Polymer({
    editParticipantDetails: function (event, detail, sender) {
      console.log('editParticipantDetails!');
      this.state.step = 'participants';
    }
  });
})();
