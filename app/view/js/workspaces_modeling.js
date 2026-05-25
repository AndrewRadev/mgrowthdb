Page('.workspaces-modeling-page', function($page) {
  let chartUrl = $page.data('chartUrl')
  let $form   = $page.find('.js-chart-form');

  let orcidId       = $page.data('orcidId');
  let workspaceName = $page.data('workspaceName');

  // TODO: Adapt to workspaces:

  let $activeRadio = $('.js-trace-row:visible input[type=radio]:checked');

  if ($activeRadio.length > 0) {
    updateChart($activeRadio.first());
    updateSelectedWorkspaceEntry($activeRadio.first());
  }

  let $pendingIndicators = $page.find('[data-modeling-state=pending]');
  if ($pendingIndicators.length > 0) {
    checkForUpdates();
  }

  $page.find('.js-coefficients-select,.js-fit-select').each(function() {
    let $select = $(this);

    $select.select2({
      multiple: true,
      theme: 'custom',
      width: '100%',
      templateResult: select2WithDescription,
    });

    $select.trigger('change');
  });

  $page.find('.js-experiment-container').each(function(e) {
    let $container = $(this);

    if ($container.find('input[type=checkbox]:checked').length > 0) {
      $container.removeClass('hidden');
      return;
    }
  });

  $page.on('change', 'form.js-modeling-form', function(e) {
    let $form = $(e.currentTarget);

    let $activeRadio = $page.find('.js-trace-row:visible input[type=radio]:checked');

    if ($activeRadio.length > 0) {
      updateChart($activeRadio.first());
      updateSelectedWorkspaceEntry($activeRadio.first());
    }
  });

  $page.on('submit', '.js-modeling-form', function(e) {
    e.preventDefault();
    let $form = $(e.currentTarget);

    let $activeRow = $('.js-trace-row.highlight:visible');

    $.ajax({
      url: $form.attr('action'),
      dataType: 'json',
      method: 'POST',
      data: $form.serializeArray(),
      success: function(response) {
        let modelingResultId = response.modelingResultId;

        if ($activeRow.find('[data-modeling-result-id]').length == 0) {
          $activeRow.append(`<div data-modeling-result-id="${modelingResultId}">⏳</div>`);
        }

        checkForUpdates();
      }
    })
  });

  $page.on('click', '.js-toggle-published', function(e) {
    e.preventDefault();

    let $button = $(e.currentTarget);
    let url     = $button.data('url');

    $form.find('input').prop('disabled', true);

    $.ajax({
      url: url,
      dataType: 'json',
      method: 'POST',
      success: function(response) {
        $form.find('input').prop('disabled', false);
        let $activeRadio = $('.js-trace-row:visible input[type=radio]:checked');
        updateChart($activeRadio.first());
      },
      error: function() {
        $form.find('input').prop('disabled', false);
      }
    })
  });

  $page.on('click', '.js-edit-model', function(e) {
    let $parentContainer = $(this).parents('.js-preview');
    let $form = $parentContainer.next('form[data-custom-model-id]');

    $parentContainer.addClass('hidden');
    $form.removeClass('hidden');
  });

  $page.on('click', '.js-cancel-edit-model', function(e) {
    let $form = $(this).parents('form[data-custom-model-id]');
    let $preview = $form.prev('.js-preview');

    $form.addClass('hidden');
    $preview.removeClass('hidden');
  });

  $page.on('click', '.js-delete-model', function(e) {
    let $button = $(this);

    if (confirm($button.data('confirm'))) {
      $.ajax({
        url: $button.data('url'),
        method: 'POST',
        success: function() {
          window.location.reload();
        }
      });
    }
  });

  function updateMeasurementSubjects($form) {
    let $techniqueSelect = $form.find('.js-technique-type');
    let techniqueId = $techniqueSelect.val();

    $form.find('[data-technique-id]').addClass('hidden')
    $form.find(`[data-technique-id=${techniqueId}]`).removeClass('hidden')
  }

  function updateChart($radio) {
    let $form = $radio.parents('form');
    $form.find('input').prop('disabled', true);

    let $chart       = $form.find('.js-chart');
    let modelingType = $form.find('select[name=modelingType]').val();
    let logTransform = $form.find('input[name=logTransform]').prop('checked');
    let isPublished  = $form.find('input[name=isPublished]').prop('checked');

    $page.find('.js-trace-row').removeClass('highlight');
    $radio.parents('.js-trace-row').addClass('highlight');

    let workspaceEntryId = $radio.val().replaceAll('workspaceEntry|', '');

    $.ajax({
      url: chartUrl,
      dataType: 'html',
      data: {
        modelingType:     modelingType,
        logTransform:     logTransform,
        isPublished:      isPublished,
        workspaceEntryId: workspaceEntryId,
      },
      success: function(response) {
        $chart.html(response)
        $form.find('input').prop('disabled', false);
        initTooltips();
      },
      error: function() {
        $form.find('input').prop('disabled', false);
      }
    });
  }

  function updateSelectedWorkspaceEntry($radio) {
    let radioValue       = $radio.val();
    let measurementLabel = $radio.data('measurementLabel');
    let unitsLabel       = $radio.data('unitsLabel');
    let workspaceEntryId = parseInt(radioValue.replaceAll('workspaceEntry|', ''), 10);

    $page.find('input[name=selectedWorkspaceEntryId]').val(workspaceEntryId);
    $page.find('.js-measurement-label').html(measurementLabel);
    $page.find('.js-units-label').html(unitsLabel);
  }

  function checkForUpdates() {
    $.ajax({
      url: `/workspaces/${orcidId}/modeling/${workspaceName}/check.json`,
      dataType: 'json',
      success: function(response) {
        let $calculationResult = $page.find('.js-calculation-result');
        let allReady = true;

        for (const [resultId, resultState] of Object.entries(response)) {
          let $indicator = $page.find(`[data-modeling-result-id=${resultId}]`);

          if (resultState == 'ready') {
            $indicator.text('✅');
          } else if (resultState == 'error') {
            $indicator.text('❌');
          } else if (resultState == 'pending') {
            allReady = false;
            $indicator.text('⏳');
          }
        }

        if (allReady) {
          $calculationResult.html("Calculations finished. Submit the form to perform another calculation");

          let $activeRadio = $page.find('.js-trace-row:visible input[type=radio]:checked');
          if ($activeRadio.length > 0) {
            updateChart($activeRadio.first());
          }
        } else {
          $calculationResult.html('⏳ Calculating...');
          setTimeout(checkForUpdates, 1000);
        }
      }
    });
  }
})
