Page('.study-visualize-page', function($page) {
  let $compareData = $(document).find('[data-compare-ids]')

  let studyId = $page.data('studyId')
  let $form   = $page.find('.js-chart-form');

  updateChart($form).then(function() {
    let checkboxesChanged = false;

    // For each row in the preview form, check if it should be initialized on
    // the left or right:
    $form.find('.js-contexts-list .js-row').each(function() {
      let $chartRow = $(this);
      let contextId = $chartRow.data('contextId');
      let $formRow = $form.find(`input[name="measurementContext|${contextId}"]`);

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

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
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
    $form.find('.js-technique-row input[type=checkbox]').prop('checked', false);

    updateChart($form)
  });

  $page.on('click', '.js-compare', function(e) {
    e.preventDefault();

    let contextIds = [];
    $('.js-contexts-list [data-context-id]').each(function() {
      contextIds.push($(this).data('contextId'));
    });

    updateCompareData('add', contextIds);
  });

  function toggleCheckboxes($button, value) {
    let $row = $button.parents('.form-row');
    let $targetRows = $row.nextUntil('.js-header-row');
    $targetRows.find('input[type=checkbox]:visible').prop('checked', value);
  }

  function updateChart($form) {
    let selectedExperimentId = $form.find('select[name="experimentId"]').val();

    $form.find('.js-experiment-container').addClass('hidden');
    $form.find('.js-technique-row').addClass('hidden');

    let $experiment = $form.find(`.js-experiment-container[data-experiment-id="${selectedExperimentId}"]`);
    $experiment.removeClass('hidden');

    let selectedOption = $form.
      find('select[name="techniqueId"] option:selected');

    let selectedTechniqueId          = selectedOption.val();
    let selectedTechniqueSubjectType = selectedOption.data('subjectType');

    $experiment.
      find(`.js-technique-row[data-technique-id="${selectedTechniqueId}"]`).
      removeClass('hidden');

    // Update chart:

    let $chart = $form.find('.chart');

    let width          = Math.floor($chart.width());
    let scrollPosition = $(document).scrollTop();

    return $.ajax({
      url: `/study/${studyId}/visualize/chart?width=${width}`,
      dataType: 'html',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        $chart.html(response);
        $(document).scrollTop(scrollPosition);
      }
    })
  }

  // TODO duplicates study.js, extract
  function updateCompareData(action, contexts, successCallback) {
    $.ajax({
      type: 'POST',
      url: `/comparison/update/${action}.json`,
      data: JSON.stringify({'contexts': contexts}),
      cache: false,
      contentType: 'application/json',
      processData: true,
      success: function(response) {
        let compareData = JSON.parse(response);

        let countText;
        if (compareData.contextCount > 0 || compareData.modelCount > 0) {
          countText = `(${compareData.contextCount + compareData.modelCount})`;
        } else {
          countText = '';
        }

        let $sidebarCompareItem = $(document).find('.js-sidebar-compare');
        $sidebarCompareItem.find('.js-count').html(countText);

        $sidebarCompareItem.addClass('highlight');
        setTimeout(function() {
          $sidebarCompareItem.removeClass('highlight');
        }, 500);

        if (successCallback) {
          successCallback(compareData);
        }
      },
    })
  }
});
