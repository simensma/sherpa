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
    },

    updateIsPassed: function (oldVal, newVal) {
      newVal = this.step.isPassed;
      if (newVal === true) {
        this.setAttribute('passed', '');
      } else {
        this.removeAttribute('passed');
      }
    },

    ready: function () {
      this.updateIsCurrent();
      this.updateIsPassed();
    }

  });
})();
