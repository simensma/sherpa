(function () {
  Polymer({

    /* Data model */

    aktivitet: undefined,
    user: undefined,
    participant: undefined,
    steps: {
      description: {
        id: 'description',
        title: 'Om aktiviteten',
        slug: 'beskrivelse',
        isCurrent: false,
        isAvailable: true,
        component: undefined
      },
      participants: {
        id: 'participants',
        title: 'Deltaker',
        slug: 'deltakere',
        isCurrent: true,
        isAvailable: false,
        component: undefined
      },
      summary: {
        id: 'summary',
        title: 'Oppsummering',
        slug: 'oppsummering',
        isCurrent: false,
        isAvailable: false,
        component: undefined
      },
      receipt: {
        id: 'receipt',
        title: 'Kvittering',
        slug: 'kvittering',
        isCurrent: false,
        isAvailable: false,
        component: undefined
      }
    },
    state: {
      step: undefined
    },


    /* Observers */

    observe: {
      'state.step': 'stateStepChanged',
      'route': 'routeChanged',
      'aktivitet': 'aktivitetChanged'
    },

    updateSteps: function (newStep) {
      for (var stepKey in this.steps) {
        this.steps[stepKey].isCurrent = false;
      }
      this.steps[newStep.id].isCurrent = true;
    },

    stateStepChanged: function (oldVal, newVal) {
      $('body').scrollTop($('[data-dnt-container="aktivitet"]').offset().top);
      this.updateSteps(this.state.step);
      window.location.hash = this.state.step.slug;
    },

    routeChanged: function (oldVal, newVal) {
      console.log('Route changed to', newVal);
    },

    aktivitetChanged: function (oldVal, newVal) {
      // console.log('aktivitetChanged!', oldVal, newVal);
    },

    handleAktivitetResponse: function (event, ajax, element) {
      // Handled by data binding to this.aktivitet
    },

    handleUserResponse: function (event, ajax, element) {
      this.user = ajax.response;
      this.participant = {
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        email: this.user.email,
        phone: this.user.phone,
        date_of_birth: this.user.dob,
        comment: undefined,
        parents_guardians: [],
        user_id: this.user.id
      };

      if (this.user.is_member) {
        this.participant.memberid = this.user.memberid;
      }
    },

    /* Lifecycle methods */

    ready: function () {

      // Set aktivitet AJAX URL
      try {
        this.shadowRoot.querySelector('core-ajax#aktivitet_ajax').setAttribute('url', '/api/v2/aktivitet/' + this.aktivitet_id);
      } catch (e) {
        console.error(e);
      }

      // Set user AJAX URL
      try {
        this.shadowRoot.querySelector('core-ajax#user_ajax').setAttribute('url', '/api/v2/user/' + this.user_id);
      } catch (e) {
        console.error(e);
      }


      // Set intial step
      this.state.step = this.steps.participants;

      this.removeAttribute('hidden');

    }

  });
})();
