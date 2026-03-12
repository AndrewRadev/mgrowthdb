Page('.upload-page .step-content.active', function($page) {
  // Don't do any fancy scrolling on page reload, if possible:
  // Reference: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceEntry
  let isReload =
    window.performance.getEntriesByType('navigation')[0]?.type === 'reload' ||
    window.performance.navigation?.type === 1; // fallback for old browsers

  // If there is an error, scroll to it:
  let $errorMessageList = $page.find('.error-message-list');
  if ($errorMessageList.length > 0) {
    setTimeout(function() {
      $(document).scrollTo($errorMessageList, 500, {offset: -20});
    }, 1);
  } else if (!isReload) {
    // If there is a previous section status, scroll to it, unless the user refreshed the page:
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
