(function () {
  Polymer({

    step: {},

    observe: {
      'step.isCurrent': 'updateIsCurrent',
      'step.isPassed': 'updateIsPassed'
    },

    updateIsCurrent: function (oldVal, newVal) {
      newVal = this.step.isCurrent;
      if (newVal === true) {
        this.setAttribute('current', '');
      } else {
        this.removeAttribute('current');
      }
      console.log('updateIsCurrent', newVal);
    },

    updateIsPassed: function (oldVal, newVal) {
      newVal = this.step.isPassed;
      if (newVal === true) {
        this.setAttribute('passed', '');
      } else {
        this.removeAttribute('passed');
      }
      console.log('updateIsPassed', newVal);
    },

    ready: function () {
      this.updateIsCurrent();
      this.updateIsPassed();
    }

  });
})();
