(function () {
  document.querySelectorAll('.rating-input').forEach(function (root) {
    var hint = root.querySelector('.rating-input__value');
    var radios = root.querySelectorAll('.rating-input__radio');

    function updateHint() {
      var selected = root.querySelector('.rating-input__radio:checked');
      if (!hint) {
        return;
      }
      if (selected) {
        hint.textContent = 'Note sélectionnée : ' + selected.value + ' sur 5';
      } else {
        hint.textContent = 'Cliquez sur une étoile pour noter (1 à 5)';
      }
    }

    radios.forEach(function (radio) {
      radio.addEventListener('change', updateHint);
    });

    updateHint();
  });
})();
