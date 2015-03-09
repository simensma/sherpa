(function () {
  Polymer({

    observe: {
      'participant.date_of_birth': 'dateOfBirthChanged'
    },

    dateOfBirthChanged: function (oldVal, newVal) {
      console.log('Participant', this.participant.name, 'date of birth changed from', oldVal, 'to', newVal);
      this.participant.is_minor = true;
    },

    ready: function () {
      console.log('Participant is ready.');
    }

  });
})();
