(function () {
  Polymer({

    member: {},

    observe: {
      'member.date_of_birth': 'dateOfBirthChanged',
      'member.date_of_birth_formatted': 'dateOfBirthFormattedChanged'
    },

    fetchMember: function () {
      var fetchMemberAjax = this.$.fetch_member_ajax;

      var requestParams = {
        memberid: this.member.memberid,
        dob: this.member.date_of_birth
      };

      fetchMemberAjax.setAttribute('url', '/api/v2/medlem/' + this.member.memberid + '/');
      fetchMemberAjax.params = JSON.stringify(requestParams);
      fetchMemberAjax.go();
    },

    handleFetchMemberError: function (e) {
      this.fetchMemberError = true;
    },

    handleFetchMemberResponse: function (event, ajax, element) {
      // TODO: If success
      var member = ajax.response.member;
      this.state.step = this.steps.receipt;
    },

    dateOfBirthChanged: function (oldVal, newVal) {
      var dateOfBirthMoment = moment(this.member.date_of_birth, 'YYYY-MM-DD', true); // Strict

      if (dateOfBirthMoment.isValid()) {
        var dateOfBirthFormatted = dateOfBirthMoment.format('DD.MM.YYYY')

        if (this.member.date_of_birth_formatted !== dateOfBirthFormatted) {
          this.member.date_of_birth_formatted = dateOfBirthFormatted;
        }
      }
    },

    dateOfBirthFormattedChanged: function (oldVal, newVal) {
      var dateOfBirthFormattedMoment = moment(this.member.date_of_birth_formatted, 'DD.MM.YYYY', true); // Strict

      if (dateOfBirthFormattedMoment.isValid()) {
        if (oldVal === newVal) {
          return;
        }
        this.member.date_of_birth = dateOfBirthFormattedMoment.format('YYYY-MM-DD');
      }
    }

  });
})();
