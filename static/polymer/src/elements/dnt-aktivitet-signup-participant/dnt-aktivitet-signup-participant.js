(function () {
  Polymer({

    AGE_MINOR_LIMIT: 16,
    PARENTS_GUARDIANS_LIMIT: 2,

    user_contact_info_has_changed: false,
    user: {},
    participant: {},
    membership_alert_is_dismissed: false,
    is_valid: false,

    observe: {
      'participant.first_name': 'userContactInfoChanged',
      'participant.last_name': 'userContactInfoChanged',
      'participant.email': 'userContactInfoChanged',
      'participant.phone': 'userContactInfoChanged',
      'participant.date_of_birth': 'dateOfBirthChanged',
      'participant.date_of_birth_formatted': 'dateOfBirthFormattedChanged',
      '$.input_participant_first_name.validity.valid': 'validateView',
      '$.input_participant_last_name.validity.valid': 'validateView',
      '$.input_participant_date_of_birth.validity.valid': 'validateView',
      'is_valid': 'isValidChanged'
    },

    validateView: function () {
      var requiredToValidate = [
        this.$.input_participant_first_name_decorator,
        this.$.input_participant_last_name_decorator,
        this.$.input_participant_date_of_birth_decorator,
        this.$.input_participant_phone_decorator,
        this.$.input_participant_email_decorator
      ];

      for (var i = 0; i < requiredToValidate.length; i++) {
        var isValid = requiredToValidate[i].validate();
      }

      var isValid = (requiredToValidate.indexOf(false) > -1) ? false : true;
      this.is_valid = isValid;
    },

    userContactInfoChanged: function () {
      var userFirstNameHasChanged = this.participant.first_name !== this.user.first_name;
      var userLastNameHasChanged = this.participant.last_name !== this.user.last_name;
      var userPhoneHasChanged = this.participant.phone !== this.user.phone_mobile;
      var userEmailHasChanged = this.participant.email !== this.user.email;

      if (userFirstNameHasChanged || userLastNameHasChanged || userPhoneHasChanged || userEmailHasChanged) {
        this.user_contact_info_has_changed = true;

      } else {
        this.user_contact_info_has_changed = false;
      }

      this.$.input_participant_first_name_decorator.updateLabelVisibility(this.participant.first_name);
      this.$.input_participant_last_name_decorator.updateLabelVisibility(this.participant.last_name);
      this.$.input_participant_phone_decorator.updateLabelVisibility(this.participant.phone);
      this.$.input_participant_email_decorator.updateLabelVisibility(this.participant.email);
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

      // Make sure label is set visible
      this.$.input_participant_date_of_birth_decorator.updateLabelVisibility(this.participant.date_of_birth_formatted);

      var dateOfBirthFormattedMoment = moment(this.participant.date_of_birth_formatted, 'DD.MM.YYYY', true); // Strict

      if (dateOfBirthFormattedMoment.isValid()) {

        if (oldVal === newVal) {
          return;
        }

        this.participant.date_of_birth = dateOfBirthFormattedMoment.format('YYYY-MM-DD');
      }

    },

    becomeMember: function () {
      window.location.href = "/innmelding/registrering/";
    },

    dismissMembershipAlert: function () {
      this.membership_alert_is_dismissed = true;
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

    associateUserWithMember: function () {
      this.dismissMembershipAlert();
      this.participant.is_unconfirmed_member = true;
    },

    updateUserContactInformation: function () {
      // TODO: Implement this
      console.log('TODO: Will update user contact information!');
    }

  });
})();
