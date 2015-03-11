(function () {
  Polymer({

    AGE_MINOR_LIMIT: 16,

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

      var todayMoment = moment(); // Today
      var dateOfBirthMoment = moment(this.participant.date_of_birth, 'DD.MM.YYYY', true); // Strict

      if (dateOfBirthMoment.isValid()) {
        var participantAge = todayMoment.diff(dateOfBirthMoment, 'years'); // Float
        this.participant.is_minor = (participantAge < this.AGE_MINOR_LIMIT) ? true : false;
      }

    },

    addParentGuardian: function () {
      this.participant.parents_guardians.push({
        name: '',
        email: '',
        phone: '',
        address: '',
        zipcode: '',
        city: ''
      });
    },

    addParticipantComment: function () {
      this.participant.comment = '';
    }

  });
})();
