Page('.upload-page .step-content.active', function($page) {
  // If there is an error, scroll to it:
  let $errorMessageList = $page.find('.error-message-list');
  if ($errorMessageList.length > 0) {
    setTimeout(function() {
      $(document).scrollTo($errorMessageList, 500, {offset: -20});
    }, 1);
  } else {
    // If there is a previous section status, scroll to it:
    let $previousSection = $page.prev('.step-content');
    if ($previousSection.length > 0) {
      setTimeout(function() {
        $(document).scrollTo($previousSection, 500);
      }, 1);
    }
  }

  $page.on('submit', '.js-step-form', function() {
    $page.find('.loader-image-container').removeClass('hidden');
  });
})
