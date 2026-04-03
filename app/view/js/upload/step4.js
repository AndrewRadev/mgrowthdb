Page('.upload-page .step-content.step-4.active', function($step4) {
  $step4.find('.js-compartment-section').initAjaxSubform({
    urlParams: { subform_type: 'compartment' },

    prefixRegex:    /compartments-(\d+)-/,
    prefixTemplate: 'compartments-{}-',

    buildSubform: function (index) {
      let templateHtml = $('template.compartment-form').html();
      let $newForm = $("<div />").html(templateHtml).children();

      $newForm.addPrefix(`compartments-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform, index) {
      $subform.on('change', 'input[name$="name"]', function() {
        updateIndexAndName($subform, index + 1, $(this));
      });
      updateIndexAndName($subform, index + 1, null);
    },

    onDuplicate: function($newForm) {
      // Reset name
      $newForm.find('input[name$="name"]').val('');
      $newForm.find('.js-title').html('[New]')
    },
  });

  $step4.find('.js-community-section').initAjaxSubform({
    urlParams: { subform_type: 'community' },

    prefixRegex:    /communities-(\d+)-/,
    prefixTemplate: 'communities-{}-',

    buildSubform: function (index) {
      let templateHtml = $('template.community-form').html();
      let $newForm = $("<div />").html(templateHtml).children();

      $newForm.addPrefix(`communities-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform, index) {
      let $select = $subform.find('.js-strain-select');

      $select.select2({
        multiple: true,
        theme: 'custom',
        width: '100%',
        templateResult: select2Highlighter,
      });

      $select.trigger('change');
    },

    onDuplicate: function($newForm) {
      // Reset name
      $newForm.find('input[name$="name"]').val('');
    },
  });

  function updateIndexAndName($container, index, $nameInput) {
    let $index = $container.find('.js-index');
    let $title = $container.find('.js-title');

    $index.html(index);
    if ($nameInput) {
      $title.html($nameInput.val());
    }
  }
});
