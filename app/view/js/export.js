Page('.export-page', function($page) {
  let studyId = $page.data('studyId');
  let select2Selectors = '.js-strain-select,.js-metabolite-select'

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

  $page.on('change', '.js-export-options-inputs input,select', updateFilter)
  $page.on('keyup', 'input[name=q]', _.debounce(updateFilter, 200));
  $page.on('change', select2Selectors, updateFilter)
  $page.on('click', '.js-filter-form .js-reset', function() {
    let $form = $(this).parents('form');

    $form.find('input[name=q]').val(null);
    $form.find(select2Selectors).each(function() {
      $(this).val(null).trigger('change');
    });

    setTimeout(updateFilter, 1);
  });

  $page.on('change', '.js-experiment-form', updatePreview);
  $page.on('keyup', 'input[name=custom_delimiter]', updatePreview);

  updateFilter();

  $page.on('focus', 'input[name=custom_delimiter]', function() {
    $page.find('input[name=delimiter][value=custom]').prop('checked', true);
  });

  $page.on('click', '.js-select-all', function() {
    let $form = $(this).parents('form');

    $form.find('.section-experiment input[type=checkbox]').prop('checked', true);
    updatePreview();
  });

  $page.on('click', '.js-select-average', function() {
    let $form = $(this).parents('form');

    $form.find('.section-experiment input[type=checkbox]').prop('checked', false);
    $form.find('.section-experiment input[type=checkbox].js-average').prop('checked', true);
    updatePreview();
  });

  $page.on('click', '.js-select-none', function() {
    let $form = $(this).parents('form');

    $form.find('.section-experiment input[type=checkbox]').prop('checked', false);
    updatePreview();
  });

  function updateFilter() {
    let $filterForm  = $page.find('.js-filter-form');
    let $experimentForm = $page.find('.js-experiment-form');

    let $searchInput = $filterForm.find('input[name=q]');
    let $headingLoader = $page.find('.js-experiments-heading .inline-loader-image');

    $searchInput.addClass('loading-input');
    $headingLoader.removeClass('hidden');

    $filterForm.ajaxSubmit({
      success: function(response) {
        $experimentForm.html(response);
        $searchInput.removeClass('loading-input');
        $headingLoader.addClass('hidden');
        updatePreview();
      }
    });
  }

  function updatePreview() {
    // Form with CSV options:
    let $filterForm = $page.find('.js-filter-form');

    // Form with bioreplicates:
    let $experimentForm = $page.find('.js-experiment-form');

    let data = $filterForm.serializeArray();
    data.push(...$experimentForm.serializeArray());

    let $headingLoader = $page.find('.js-preview-heading .inline-loader-image');
    $headingLoader.removeClass('hidden');

    $.ajax({
      url: `/study/${studyId}/export/preview`,
      method: 'POST',
      dataType: 'html',
      data: data,
      success: function(response) {
        $page.find('.js-preview').html(response);
        $headingLoader.addClass('hidden');
      }
    });
  }
});
