Page('.upload-page .step-content.active', function($page) {
  $page.on('submit', '.js-step-form', function() {
    $page.find('.loader-image-container').removeClass('hidden');
  });
})
