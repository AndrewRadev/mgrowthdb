Page('.study-page', function($page) {
  initCompareButtons($page);

  $experiments = $('.js-experiments');

  if ($experiments.length > 0) {
    $.ajax({
      url: $experiments.data('url'),
      success: function(response) {
        $experiments.html(response);
      }
    });
  }
});
