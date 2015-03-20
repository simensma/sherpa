var dateOfBirthFormatSync = {
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

  }
};
