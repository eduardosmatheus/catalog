function signInCallback(authResult) {
  if (authResult['code']) {
    $('#signinButton').attr('style', 'display: none');
    $.ajax({
      type: 'POST',
      url: 'gconnect?state={{STATE}}',
      processData: false,
      data: authResult['code'],
      contentType: 'application/octet-stream; charset=utf-8',
      success: function (result) {
        if (result) {
          $('#result').html('Login Successfull!<br>' + result + '</br>Redirecting...');
        }
        else if (authResult['error']) {
          console.log('There was an error: ' + authResult['error']);
        }
        else {
          $('#result').html('Failed to make a server-side call. Check your configuration and console.');
        }
      }
    });
  }
}