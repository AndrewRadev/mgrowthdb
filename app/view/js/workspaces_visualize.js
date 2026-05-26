Page('.workspaces-visualize-page', function($page) {
  let chartUrl = $page.data('chartUrl')
  let $form   = $page.find('.js-chart-form');

  updateChart($form).then(function() {
    let checkboxesChanged = false;

    // For each row in the preview form, check if it should be initialized on
    // the left or right:
    $form.find('.js-traces-list .js-row').each(function() {
      let $chartRow = $(this);
      let workspaceEntryId = $chartRow.data('workspaceEntryId');
      let $formRow = $form.find(`input[name="workspaceEntry|${workspaceEntryId}"]`);

      if (($formRow).is('[data-axis-right]')) {
        $chartRow.find('.js-axis-left').prop('checked', false);
        $chartRow.find('.js-axis-right').prop('checked', true);
        checkboxesChanged = true;
      }
    });

    if (checkboxesChanged) {
      updateChart($form);
    }
  });

  // Exclusive checkboxes on one row:
  $page.on('change', 'input.js-axis', function(e) {
    let $checkbox = $(e.currentTarget);
    let $row = $checkbox.parents('.js-row')
    let $blank = $row.find('.js-axis-blank');
    let $other;

    if ($checkbox.is('.js-axis-left')) {
      $other = $row.find('.js-axis-right');
    } else if ($checkbox.is('.js-axis-right')) {
      $other = $row.find('.js-axis-left');
    }

    if ($checkbox.is(':checked') && $other.is(':checked')) {
      $other.prop('checked', false);
    } else if (!$checkbox.is(':checked') && !$other.is(':checked')) {
      $blank.prop('checked', true);
      $row.addClass('blank');
    } else {
      $blank.prop('checked', false);
      $row.removeClass('blank');
    }
  });

  // Group checkboxes updated together:
  $page.on('change', 'input.js-axis-group', function(e) {
    let $checkbox = $(e.currentTarget);
    let $row = $checkbox.parents('.js-row')

    let checkboxSelector;
    let otherCheckboxSelector;

    if ($checkbox.is('.js-axis-left')) {
      checkboxSelector      = '.js-axis-left';
      otherCheckboxSelector = '.js-axis-right';
    } else if ($checkbox.is('.js-axis-right')) {
      checkboxSelector      = '.js-axis-right';
      otherCheckboxSelector = '.js-axis-left';
    }

    let $groupRows = $row.nextUntil('.js-group-row');
    $groupRows.each(function() {
      $(this).find(checkboxSelector).prop('checked', true);
      $(this).find(otherCheckboxSelector).prop('checked', false);
    });
  });

  $page.on('change', 'form.js-chart-form', function(e) {
    let $form = $(e.currentTarget);
    updateChart($form);
  });

  $page.on('click', '.js-select-all', function(e) {
    e.preventDefault();
    toggleCheckboxes($(e.currentTarget), true);
    updateChart($form)
  });

  $page.on('click', '.js-deselect-all', function(e) {
    e.preventDefault();
    toggleCheckboxes($(e.currentTarget), false);
    updateChart($form)
  });

  $page.on('click', '.js-clear-chart', function(e) {
    e.preventDefault();

    let $link = $(e.currentTarget);
    let $form = $link.parents('form');
    $form.find('.js-trace-row input[type=checkbox]').prop('checked', false);

    updateChart($form)
  });

  function toggleCheckboxes($button, value) {
    let $group = $button.parents('.js-trace-group');
    let $targetRows = $row.find('.js-trace-row');
    $targetRows.find('input[type=checkbox]:visible').prop('checked', value);
  }

  function updateChart($form) {
    let selectedSourceType = $form.find('select[name="sourceType"]').val();

    $form.find('.js-trace-row').addClass('hidden');
    $form.
      find(`.js-trace-row[data-source-type="${selectedSourceType}"]`).
      removeClass('hidden');

    // Update chart:

    let $chart = $form.find('.chart');

    let width          = Math.floor($chart.width());
    let scrollPosition = $(document).scrollTop();

    return $.ajax({
      url: `${chartUrl}?width=${width}`,
      dataType: 'html',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        $chart.html(response);
        $(document).scrollTop(scrollPosition);
      }
    })
  }
})
