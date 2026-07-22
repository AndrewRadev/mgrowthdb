Page('.study-page', function($page) {
  initCompareButtons($page);

  $experiments = $('.js-experiments');

  if ($experiments.length > 0) {
    let $searchForm  = $page.find('.js-search-form');

    $page.on('keyup', 'input[name=q]', _.debounce(updateSearch, 200));
    $page.on('change', '.js-strain-select,.js-metabolite-select,.js-modeling-type-select', updateSearch)
    $searchForm.on('reset', function() {
      setTimeout(updateSearch, 1);
    });

    // Trigger initial update on page load:
    setTimeout(updateSearch, 1);

    // Initialize select filters:
    $page.find('.js-strain-select,.js-metabolite-select,.js-modeling-type-select').each(function() {
      let $select = $(this);

      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      });

      $select.trigger('change');
    });
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
