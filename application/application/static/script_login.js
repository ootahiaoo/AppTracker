$(document).ready(function () {
    $('#register-form').submit(function (event) {
      if (checkUsernameAvailability() === false || checkPasswordConfirmation() === false) {
        event.preventDefault();
        return false;
      }
    });

    $('#register-form :input, #login-form :input').each(function () {
      $(this).on('input', function (event) {
        if (checkCharacters($(this).val()) === false) {
          this.setCustomValidity("May only use underscore, dash or alphanumeric characters.");
        } else {
          this.setCustomValidity('');
        }
        this.reportValidity();
      });
    });

    $('#confirmation-register').on('change', function (event) {
      var input = $('#confirmation-register').val();
      if (input != "" && checkCharacters(input)) {
        checkPasswordConfirmation();
      } else {
        $('#confirmation-register').removeClass('is-invalid');
      }
    });

    $('#username-register').on('change', function (event) {
      var input = $('#username-register').val();
      if (input != "" && checkCharacters(input)) {
        checkUsernameAvailability()
      } else {
        $('#username-register').removeClass('is-invalid');
      }
    });

  });

  function checkCharacters(text) {
    var regex = '^[a-zA-Z0-9_-]*$'
    var constraint = new RegExp(regex, 'i')
    return constraint.test(text)
  }

  function checkPasswordConfirmation() {
    if ($('#password-register').val() != $('#confirmation-register').val()) {
      $('#confirmation-register').addClass('is-invalid');
      return false;
    }
    $('#confirmation-register').removeClass('is-invalid');
    return true;
  }

  function checkUsernameAvailability() {
    var name = $('#username-register').val()
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
      if (ajax.readyState === 4 && ajax.status == 200) {
        if (ajax.responseText === "Not available") {
          $('#username-register').addClass('is-invalid');
        } else {
          $('#username-register').removeClass('is-invalid');
        }
      }
    };
    ajax.open("POST", "/check_username_" + name, true);
    ajax.send();
  }