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

    handleAktivitetResponse: function (event, response, element) {
      // Handled by data binding to this.aktivitet
    },

    /* Lifecycle methods */

    ready: function () {

      // Set current activity
      // this.aktivitet = {
      //   title: 'På ski i Huldreheimen'
      // };

      // Set aktivitet AJAX URL
      try {
        this.shadowRoot.querySelector('core-ajax#aktivitet').setAttribute('url', '/api/v2/aktivitet/' + this.aktivitet_id);
      } catch (e) {
        console.error(e);
      }

      // Set current user
      this.user = {
        name: 'Sara Fossen',
        email: '',
        phone: '470 11 141',
        date_of_birth: '20.10.2001',
      };

      // Set participant
      this.participant = {
        name: this.user.name,
        email: this.user.email,
        phone: this.user.phone,
        date_of_birth: this.user.date_of_birth,
        comment: undefined,
        parents_guardians: [
          {
            name: 'Sigmund Fossen',
            email: 'sigfos@gmail.com',
            phone: '970 23 445',
            address: 'Øvrevegen 5',
            zipcode: '0530',
            city: 'OSLO'
          }
        ]
      };

      // Set intial step
      this.state.step = this.steps.participants;

      this.removeAttribute('hidden');

    }

  });
})();
