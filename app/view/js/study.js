Page('.study-page', function($page) {
  initCompareButtons($page);

  let $experiments = $('.js-experiments');
  let select2Selectors = '.js-strain-select,.js-metabolite-select,.js-modeling-type-select'

  if ($experiments.length > 0) {
    let $filterForm  = $page.find('.js-filter-form');

    $page.on('keyup', 'input[name=q]', _.debounce(updateFilter, 200));
    $page.on('change', select2Selectors, updateFilter)

    $filterForm.on('submit', function(e) {
      e.preventDefault();
      updateFilter();
    });
    $filterForm.on('reset', function() {
      $page.find(select2Selectors).each(function() {
        $(this).val(null).trigger('change');
      });

      setTimeout(updateFilter, 1);
    });

    // Trigger initial update on page load:
    setTimeout(updateFilter, 1);

    // Initialize select filters:
    $page.find(select2Selectors).each(function() {
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

  function updateFilter() {
    let $filterForm  = $page.find('.js-filter-form');
    let $experiments = $page.find('.js-experiments');

    let $searchInput = $filterForm.find('input[name=q]');
    $searchInput.addClass('loading-input');

    $filterForm.ajaxSubmit({
      success: function(response) {
        $experiments.html(response);
        $searchInput.removeClass('loading-input');
        initTooltips();
      }
    });
  }
});
