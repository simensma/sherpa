(function () {
  Polymer(Polymer.mixin({

    member: {},

    observe: {
      'participant.date_of_birth': 'dateOfBirthChanged',
      'participant.date_of_birth_formatted': 'dateOfBirthFormattedChanged'
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
    }

  }, dateOfBirthFormatSync));
})();
