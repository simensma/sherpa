(function () {
  Polymer({

    AGE_MINOR_LIMIT: 16,
    PARENTS_GUARDIANS_LIMIT: 2,

    user_contact_info_has_changed: false,
    is_valid: true,
    user: {},
    participant: {},

    observe: {
      'participant.first_name': 'userContactInfoChanged',
      'participant.last_name': 'userContactInfoChanged',
      'participant.email': 'userContactInfoChanged',
      'participant.phone': 'userContactInfoChanged',
      'participant.date_of_birth': 'dateOfBirthChanged',
      'participant.date_of_birth_formatted': 'dateOfBirthFormattedChanged'
    },

    userContactInfoChanged: function () {
      var userFirstNameHasChanged = this.participant.first_name !== this.user.first_name;
      var userLastNameHasChanged = this.participant.last_name !== this.user.last_name;
      var userPhoneHasChanged = this.participant.phone !== this.user.phone;
      var userEmailHasChanged = this.participant.email !== this.user.email;

      if (userFirstNameHasChanged || userLastNameHasChanged || userPhoneHasChanged || userEmailHasChanged) {
        this.user_contact_info_has_changed = true;

      } else {
        this.user_contact_info_has_changed = false;
      }
    },

    dateOfBirthChanged: function (oldVal, newVal) {

      var todayMoment = moment(); // Today
      var dateOfBirthMoment = moment(this.participant.date_of_birth, 'YYYY-MM-DD', true); // Strict

      if (dateOfBirthMoment.isValid()) {
        var dateOfBirthFormatted = dateOfBirthMoment.format('DD.MM.YYYY')

        if (this.participant.date_of_birth_formatted !== dateOfBirthFormatted) {
          this.participant.date_of_birth_formatted = dateOfBirthFormatted;
        }

        var participantAge = todayMoment.diff(dateOfBirthMoment, 'years'); // Float
        this.participant.is_minor = (participantAge < this.AGE_MINOR_LIMIT) ? true : false;
      }

    },

    dateOfBirthFormattedChanged: function (oldVal, newVal) {

      var dateOfBirthFormattedMoment = moment(this.participant.date_of_birth_formatted, 'DD.MM.YYYY', true); // Strict

      if (dateOfBirthFormattedMoment.isValid()) {

        if (oldVal === newVal) {
          return;
        }

        this.participant.date_of_birth = dateOfBirthFormattedMoment.format('YYYY-MM-DD');
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

    removeParentGuardian: function (event, detail, sender) {
      var parentGuardianToRemove = sender.templateInstance.model.parent_guardian;
      var allParentsGuardians = this.participant.parents_guardians;
      var parentGuardianToRemoveIndex = allParentsGuardians.indexOf(parentGuardianToRemove);
      allParentsGuardians.splice(parentGuardianToRemoveIndex, 1);
    },

    addParticipantComment: function () {
      this.participant.comment = '';
    },

    ready: function () {
      // console.log('ready!');
      // console.log(this.querySelectorAll('paper-input-decorator'));
    },

    updateUserContactInformation: function () {
      console.log('Will update user contact information!');
    }

  });
})();
