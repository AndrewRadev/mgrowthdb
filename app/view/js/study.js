Page('.study-page', function($page) {
  initCompareButtons($page);

  $experiments = $('.js-experiments');

  if ($experiments.length > 0) {
    let $searchForm  = $page.find('.js-search-form');

    $page.on('keyup', 'input[name=q]', _.debounce(updateSearch, 200));
    $searchForm.on('reset', function() {
      setTimeout(updateSearch, 1);
    });

    // Trigger initial update on page load:
    setTimeout(updateSearch, 1);
  }

  function updateSearch() {
    let $searchForm  = $page.find('.js-search-form');
    let $experiments = $page.find('.js-experiments');

    let $searchInput = $searchForm.find('input[name=q]');
    $searchInput.addClass('loading-input');

    $searchForm.ajaxSubmit({
      success: function(response) {
        $experiments.html(response);
        $searchInput.removeClass('loading-input');
      }
    });
  }
});
