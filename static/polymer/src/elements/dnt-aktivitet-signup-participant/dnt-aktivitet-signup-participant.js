(function () {
  Polymer({

    user_contact_info_has_changed: false,
    user: {},
    participant: {},

    observe: {
      'participant.name': 'userContactInfoChanged',
      'participant.email': 'userContactInfoChanged',
      'participant.phone': 'userContactInfoChanged',
      'participant.date_of_birth': 'dateOfBirthChanged'
    },

    userContactInfoChanged: function () {
      var userNameHasChanged = this.participant.name !== this.user.name;
      var userPhoneHasChanged = this.participant.phone !== this.user.phone;
      var userEmailHasChanged = this.participant.email !== this.user.email;

      if (userNameHasChanged || userPhoneHasChanged || userEmailHasChanged) {
        this.user_contact_info_has_changed = true;

      } else {
        this.user_contact_info_has_changed = false;
      }
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
