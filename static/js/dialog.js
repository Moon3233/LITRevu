(function () {
  function openDialog(id) {
    var dialog = document.getElementById(id);
    if (dialog && typeof dialog.showModal === 'function') {
      dialog.showModal();
    }
  }

  function closeDialog(id) {
    var dialog = document.getElementById(id);
    if (dialog) {
      dialog.close();
    }
  }

  document.querySelectorAll('[data-open-dialog]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openDialog(btn.getAttribute('data-open-dialog'));
    });
  });

  document.querySelectorAll('[data-close-dialog]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      closeDialog(btn.getAttribute('data-close-dialog'));
    });
  });

  document.querySelectorAll('dialog').forEach(function (dialog) {
    dialog.addEventListener('cancel', function (event) {
      event.preventDefault();
      dialog.close();
    });
    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  });
})();
