(function () {
  Polymer({

    observe: {
      'state.step': 'stateStepChanged'
    },

    stateStepChanged: function (oldVal, newVal) {
      $('body').scrollTop($('[data-dnt-container="aktivitet"]').offset().top);
    },

    /* Data model */

    ready: function () {
      this.aktivitet = {
        title: 'På ski i Huldreheimen'
      };

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

      this.participants = [];
      this.participants.push(this.user);

      this.participant = this.user;

      this.actions = {
        goToStep: function (step) {
          console.log('going to step...', step);
          this.state.step = step;
        }
      };

      this.state = {
        step: 'participants'
      };
    }

  });
})();
