Page('.upload-page .step-content.step-5.active', function($step5) {
  $step5.find('.js-tab-1-container').initAjaxSubform({
    prefixRegex:    /experiments-(\d+)-/,
    prefixTemplate: 'experiments-{}-',

    buildSubform: function(experimentIndex) {
      let templateHtml = $('template.experiment-form').html();
      let $newForm = $("<div />").html(templateHtml).children();

      $newForm.addPrefix(`experiments-${experimentIndex}-`);

      return $newForm;
    },

    initializeSubform: function($experimentForm, experimentIndex) {
      // Initialize compartments:
      let $select = $experimentForm.find('.js-compartment-select');
      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      })
      $select.trigger('change');

      // Initialize bioreplicate subforms:
      $experimentForm.find('.js-bioreplicate-form-row').initClientSideSubform({
        buildSubform: function(bioreplicateIndex) {
          let templateHtml = $experimentForm.find('template.bioreplicate-form').html();
          let $bioreplicateForm = $("<div />").html(templateHtml).children();

          $bioreplicateForm.addPrefix(`experiments-${experimentIndex}-bioreplicates-${bioreplicateIndex}-`);

          return $bioreplicateForm;
        },

        beforeAdd: function($bioreplicateForm) {
          // Find a previous bioreplicate's name to increment its numeric suffix
          let lastName = $experimentForm.
            find('.js-bioreplicate-subform-list .js-subform-container input[name$="-name"]').
            last().
            val();

          if (!lastName || lastName == '') {
            // Find the experiment name, we can take it and add a numeric suffix
            let experimentName = $experimentForm.
              find('input[name$="-name"]').
              last().
              val();

            if (experimentName && experimentName != '') {
              lastName = `${experimentName}_0`;
            }
          }

          if (!lastName || lastName == '') {
            // No previous name found, leave it blank
            return;
          }

          let newName = lastName.replace(/\d+$/, function(m) {
            return parseInt(m, 10) + 1
          });

          if (newName == lastName) {
            newName += '_1';
          }

          $bioreplicateForm.find('input[name$="-name"]').val(newName);
        }
      });

      // Initialize perturbation subforms:
      $experimentForm.find('.js-perturbation-form-row').initClientSideSubform({
        buildSubform: function(perturbationIndex) {
          let templateHtml = $experimentForm.find('template.perturbation-form').html();
          let $perturbationForm = $("<div />").html(templateHtml).children();

          $perturbationForm.addPrefix(`experiments-${experimentIndex}-perturbations-${perturbationIndex}-`);

          return $perturbationForm;
        },

        initializeSubform: function($perturbationForm) {
          $perturbationForm.find('.js-single-select').select2({
            theme: 'custom',
            width: '100%',
            templateResult: select2Highlighter,
          })
        }
      });
    },

    onDuplicate: function($newForm) {
      // Reset names (including for bioreplicates)
      $newForm.find('input[name$="name"]').val('');

      // Remove name and number from title:
      $newForm.find('.js-name').html('[...]');
      $newForm.find('.js-index').html('[New]');

      // Remove public IDs and reset published state:
      $newForm.find('.js-public-id').remove();
      $newForm.find('.js-is-published').addClass('hidden');
      $newForm.find('.js-not-published').removeClass('hidden');

      // Remove preview state:
      let $editButton = $newForm.log().find('.js-edit-experiment');
      if (!$editButton.hasClass('hidden')) {
        $saveButton      = $newForm.find('.js-save-edit-experiment');
        $duplicateButton = $newForm.find('.js-duplicate-in-preview');

        $newForm.find('.js-preview').addClass('hidden');
        $newForm.find('.js-subform').removeClass('hidden');

        $editButton.addClass('hidden');
        $duplicateButton.addClass('hidden');
        $saveButton.removeClass('hidden');
      }
    },
  })

  $step5.on('click', '.js-tab a', function(e) {
    e.preventDefault();

    let $trigger = $(this).parents('.js-tab');

    $step5.find('.js-tab').removeClass('current');
    $trigger.addClass('current');

    if ($trigger.is('.js-tab-1')) {
      $step5.find('.js-tab-1-container').removeClass('hidden');
      $step5.find('.js-tab-2-container').addClass('hidden');
    } else if ($trigger.is('.js-tab-2')) {
      $step5.find('.js-tab-1-container').addClass('hidden');
      $step5.find('.js-tab-2-container').removeClass('hidden');
    }
  });

  $step5.on('click', '.js-edit-experiment', function() {
    $button = $(this);

    $container       = $button.parents('.js-subform-container');
    $saveButton      = $container.find('.js-save-edit-experiment');
    $duplicateButton = $container.find('.js-duplicate-in-preview');

    $container.find('.js-preview').addClass('hidden');
    $container.find('.js-subform').removeClass('hidden');

    $button.addClass('hidden');
    $saveButton.removeClass('hidden');
    $duplicateButton.removeClass('hidden');
  });

  if ($step5.find('.js-experiment-container').length == 0) {
    // By default, add one form
    $step5.find('.js-add-experiment').trigger('click');
  }

  // Clear experiments:
  $step5.on('click', '.js-clear-experiments', function(e) {
    e.preventDefault();

    let $button = $(this);

    if (confirm("This will delete all described experiments so you can enter them again. Are you sure?")) {
      $.ajax({
        url: $button.attr('data-url'),
        method: 'POST',
        success: function() {
          $('.js-subform-list').html();
        }
      });
    }
  });

  // Batch experiments:
  let $batchExperimentForm = $step5.find('.js-batch-experiment-form');

  // Initialize compartments:
  let $select = $batchExperimentForm.find('.js-compartment-select');
  $select.select2({
    multiple: true,
    theme: 'custom',
    width: '100%',
    templateResult: select2Highlighter,
  })
  $select.trigger('change');

  // Initialize perturbation subforms:
  $batchExperimentForm.find('.js-perturbation-form-row').initClientSideSubform({
    buildSubform: function(perturbationIndex) {
      let templateHtml = $batchExperimentForm.find('template.perturbation-form').html();
      let $perturbationForm = $("<div />").html(templateHtml).children();

      $perturbationForm.addPrefix(`batch-experiment-perturbations-${perturbationIndex}-`);

      return $perturbationForm;
    },

    initializeSubform: function($perturbationForm) {
      $perturbationForm.find('.js-single-select').select2({
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      })
    }
  });

  function updateBatchFormPreview() {
    let treatmentLabels = ($batchExperimentForm.find('input[name=treatmentLabels]').val() || '').split(',');
    let treatmentValues = ($batchExperimentForm.find('input[name=treatmentValues]').val() || '').split(',');

    // If there are no elements, there will be a single empty string:
    let firstLabel = treatmentLabels[0];
    let firstValue = treatmentValues[0];

    let $previewCount       = $batchExperimentForm.find('.js-preview-count');
    let $namePreview        = $batchExperimentForm.find('.js-preview-name');
    let $descriptionPreview = $batchExperimentForm.find('.js-preview-description');

    if (firstLabel != '' || firstValue != '') {
      let totalCount = Math.max(treatmentLabels.length, 1) * Math.max(treatmentValues.length, 1)
      $previewCount.html(`
        This will add <strong>${totalCount}</strong> new experiments, one for each pair of treatment label and value.
      `);

      let nameTemplate = $.trim($batchExperimentForm.find('input[name=nameTemplate]').val());
      let nameExample = nameTemplate.
        replaceAll('{treatmentLabel}', firstLabel).
        replaceAll('{treatmentValue}', firstValue);
      $namePreview.html(nameExample);

      let descriptionTemplate = $.trim($batchExperimentForm.find('textarea[name=descriptionTemplate]').val());
      let descriptionExample = descriptionTemplate.
        replaceAll('{treatmentLabel}', firstLabel).
        replaceAll('{treatmentValue}', firstValue);
      $descriptionPreview.html(descriptionExample);
    } else {
      $previewCount.html(`
        Enter at least one treatment label or value to see previews of the effects
      `);
      $namePreview.html('N/A');
      $descriptionPreview.html('N/A');
    }
  }

  // Preview batch experiment form
  $batchExperimentForm.on('keyup', '.js-preview-trigger', _.debounce(updateBatchFormPreview, 500));
  $batchExperimentForm.on('change', '.js-preview-trigger', updateBatchFormPreview);
  $batchExperimentForm.on('focus', '.js-preview-trigger', updateBatchFormPreview);
  updateBatchFormPreview();
});
