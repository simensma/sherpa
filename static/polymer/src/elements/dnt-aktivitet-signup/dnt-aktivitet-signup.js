(function () {
  Polymer({

    /* Data model */

    aktivitet: undefined,
    user: undefined,
    participant: undefined,
    state: {
      step: undefined
    },


    /* Observers */

    observe: {
      'state.step': 'stateStepChanged',
      'route': 'routeChanged'
    },

    stateStepChanged: function (oldVal, newVal) {
      $('body').scrollTop($('[data-dnt-container="aktivitet"]').offset().top);
    },

    routeChanged: function (oldVal, newVal) {
      console.log('Route changed to', newVal);
    },


    /* Lifecycle methods */

    ready: function () {

      // Set current activity
      this.aktivitet = {
        title: 'På ski i Huldreheimen'
      };

      // Set current user
      this.user = {
        name: 'Sara Fossen',
        email: '',
        phone: '470 11 141',
        date_of_birth: '20.10.2001',
        parents_guardians: [
          {
            name: 'Sigmund Fossen',
            email: 'sigfos@gmail.com',
            phone: '970 23 445'
          }
        ]
      };

      // Set participant
      this.participant = this.user;

      // Set intial step
      this.state.step = 'participants';

    }

  });
})();
