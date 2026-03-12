Page('.upload-page .step-content.step-3.active', function($step3) {
  $step3.initAjaxSubform({
    prefixRegex:    /techniques-(\d+)-/,
    prefixTemplate: 'techniques-{}-',

    addNewSubform: function ($subformList, $button, $newSubform) {
      $button.parents('.js-button-row').before($newSubform);
    },

    buildSubform: function (index, $addButton) {
      let templateHtml;

      if ($addButton.is('.js-add-bioreplicate')) {
        templateHtml = $('template.bioreplicate-form').html();
      } else if ($addButton.is('.js-add-strains')) {
        templateHtml = $('template.strain-form').html();
      } else if ($addButton.is('.js-add-metabolites')) {
        templateHtml = $('template.metabolite-form').html();
      }

      let $newForm = $("<div />").html(templateHtml).children();
      $newForm.addPrefix(`techniques-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform) {
      let subjectType = $subform.data('subjectType');

      $subform.on('change', '.js-type-select', function() {
        let $typeSelect = $(this);

        // Specific types of measurements require specific units:
        updateUnitSelect($subform, $typeSelect);

        // Specific types of measurements have different input options
        updateExtraInputs($subform, $typeSelect);
      });
      updateExtraInputs($subform, $subform.find('.js-type-select'));

      // When the type or unit of measurement change, generate preview:
      $subform.on('change', '.js-preview-trigger', function() {
        updateTitleAndPreview($subform, subjectType);
      });
      updateTitleAndPreview($subform, subjectType);

      // If there is a metabolite dropdown, set up its behaviour
      $subform.find('.js-metabolites-select').each(function() {
        let $select = $(this);

        $select.select2({
          multiple: true,
          theme: 'custom',
          width: '100%',
          minimumInputLength: 1,
          ajax: {
            url: '/metabolites/completion/',
            dataType: 'json',
            delay: 100,
            cache: true,
          },
          templateResult: select2Highlighter,
        });

        $select.trigger('change');
      });
    },
  });

  function updateUnitSelect($container, $typeSelect) {
    let $unitsSelect = $container.find('.js-unit-select');
    let type = $typeSelect.val();

    if (type == 'ph' || type == 'od') {
      $unitsSelect.val('');
    } else if (type == '16s') {
      $unitsSelect.val('reads');
    } else if (type == 'plates') {
      $unitsSelect.val('CFUs/mL');
    } else if (type == 'fc') {
      $unitsSelect.val('Cells/mL');
    }
  }

  function updateExtraInputs($container, $typeSelect) {
    let type = $typeSelect.val();

    if (type == 'fc' || type == '16s' || type == 'qpcr') {
      $container.find('.js-extra-inputs').show()
    } else {
      $container.find('.js-extra-inputs').hide().find(':checkbox').prop('checked', false);
    }
  }

  function updateTitleAndPreview($container, subjectType) {
    let $title = $container.find('.js-title');
    let $typeSelect = $container.find('.js-type-select');

    let columnName     = $typeSelect.find('option:selected').data('columnName');
    let includeStd     = $container.find('.js-include-std').is(':checked');
    let includeUnknown = $container.find('.js-include-unknown').is(':checked');

    let label = $container.find('.js-label').val().trim();
    if (label == '') {
      label = null;
    } else {
      label = '(' + label + ')'
    }

    let cellTypes = [];
    if ($container.find('.js-include-live').is(':checked')) cellTypes.push('live');
    if ($container.find('.js-include-dead').is(':checked')) cellTypes.push('dead');
    if ($container.find('.js-include-total').is(':checked')) cellTypes.push('total');

    let titleSubject = null;
    let previewSubject = null;

    if (subjectType == 'bioreplicate') {
      titleSubject = 'Community';
      previewSubject = 'Community';
    } else if (subjectType == 'strain') {
      titleSubject = 'Strain';
      previewSubject = '<strain name>';
    } else if (subjectType == 'metabolite') {
      titleSubject = 'Metabolites';
      previewSubject = '<metabolite name>';
      columnName = null;
    }

    let columnNames = []

    // General name for the title, ignoring types:
    let techniqueTitle = [titleSubject, cellTypes.join('/'), columnName, label].filter(Boolean).join(' ');
    $title.html(_.escape(techniqueTitle))

    if (cellTypes.length == 0) {
      columnNames.push([previewSubject, columnName, label].filter(Boolean).join(' '));
    } else {
      for (let cellType of cellTypes) {
        columnNames.push([previewSubject, cellType, columnName, label].filter(Boolean).join(' '));
      }
    }

    let previewTableHeader = [];
    let previewTableBody   = [];

    previewTableHeader.push('<th>...</th>');
    previewTableBody.push('<td>...</td>');

    for (let columnName of columnNames) {
      columnName = _.escape(columnName);

      previewTableHeader.push(`<th>${columnName}</th>`);
      previewTableBody.push('<td align="center">...</td>');

      if (includeStd) {
        let stdColumnName = [columnName, 'STD'].filter(Boolean).join(' ');

        previewTableHeader.push(`<th>${stdColumnName}</th>`);
        previewTableBody.push('<td align="center">...</td>');
      }
    }

    if (includeUnknown) {
      let unknownColumnName = ['Unknown', columnName, label].filter(Boolean).join(' ');

      previewTableHeader.push(`<th>${unknownColumnName}</th>`);
      previewTableBody.push('<td align="center">...</td>');

      if (includeStd) {
        let stdColumnName = [unknownColumnName, 'STD'].filter(Boolean).join(' ');

        previewTableHeader.push(`<th>${stdColumnName}</th>`);
        previewTableBody.push('<td align="center">...</td>');
      }
    }

    previewTableHeader.push('<th>...</th>');
    previewTableBody.push('<td>...</td>');

    $container.find('.js-preview-header').html(previewTableHeader.join("\n"));
    $container.find('.js-preview-body').html(previewTableBody.join("\n"));
  }
});
