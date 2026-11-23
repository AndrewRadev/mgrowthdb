Page('.upload-page .step-content.step-4.active', function($step4) {
  $step4.find('.js-medium-section').initAjaxSubform({
    urlParams: { subform_type: 'medium' },

    prefixRegex:    /media-(\d+)-/,
    prefixTemplate: 'media-{}-',

    buildSubform: function (index) {
      let templateHtml = $('template.medium-form').html();
      let $newForm = $("<div />").html(templateHtml).children();

      $newForm.addPrefix(`media-${index}-`);

      return $newForm;
    },

    initializeSubform: function($subform, index) {
      let $nameInput = $subform.find('input[name$="name"]');
      let $urlInput  = $subform.find('input[name$="url"]');

      $nameInput.on('change', function() {
        updateIndexAndName($subform, index + 1, $(this));
        updateCompartmentMediumNames();
      });
      updateIndexAndName($subform, index + 1, null);

      let $fetchButton = $subform.find('.js-fetch-mediadive-info');

      let tooltip = tippy($fetchButton[0], {
        content: "The URL does not look like a MediaDive URL (e.g. https://mediadive.dsmz.de/medium/1)",
        trigger: 'click',
      })
      tooltip.disable();

      $fetchButton.on('click', function() {
        let mediaUrl = $urlInput.val();

        if (!mediaUrl.match(/mediadive\.dsmz\.de\/medium\/./)) {
          tooltip.enable();
          tooltip.show();
          return;
        }

        tooltip.disable();
        $urlInput.addClass('loading-input');

        $.ajax($fetchButton.data('url'), {
          method: 'POST',
          data: { url: mediaUrl, mediumIndex: index },
          success: function(response) {
            $urlInput.removeClass('loading-input');
            $nameInput.animateVal(response.mediumName);
            updateIndexAndName($subform, index + 1, $nameInput)

            let $form = $urlInput.parents('.js-subform-container');
            let $subforms = $form.find('.js-medium-component-subform-list');

            $subforms.html(response.componentHtml);
            initIngredientSelects($subforms);
          }
        });
      });

      let mediumIndex = index;
      let $mediumForm = $subform;

      // Initialize component subform
      $mediumForm.find('.js-medium-component-form-row').initClientSideSubform({
        buildSubform: function(componentIndex) {
          let templateHtml = $mediumForm.find('template.medium-component-form').html();
          let $componentForm = $("<div />").html(templateHtml).children();

          $componentForm.addPrefix(`media-${mediumIndex}-components-${componentIndex}-`);

          return $componentForm;
        },

        initializeSubform: function($componentForm, componentIndex) {
          initIngredientSelects($componentForm);
        },

        afterAdd: function($componentForm) {
          let $container = $mediumForm.find('.js-medium-component-subform-list');
          let $addBox = $container.find('.js-add-box');
          $addBox.remove();
          $container.append($addBox);

          $componentForm.find('input[name$="name"]').focus();
        }
      });
    },

    onDuplicate: function($newForm) {
      // Reset name
      $newForm.find('input[name$="name"]').val('');
      $newForm.find('.js-title').html('[New]')
    },
  });

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

  function updateIndexAndName($container, index, $nameInput) {
    let $index = $container.find('.js-index');
    let $title = $container.find('.js-title');

    $index.html(index);
    if ($nameInput) {
      $title.html($nameInput.val());
    }
  }

  function initIngredientSelects($componentForm) {
    $componentForm.find('.js-ingredients-select').each(function() {
      let $select = $(this);

      $select.select2({
        theme: 'custom',
        width: '100%',
        minimumInputLength: 1,
        ajax: {
          url: '/medium-ingredients/completion/',
          dataType: 'json',
          delay: 100,
          cache: true,
        },
        templateResult: select2Highlighter,
      });
      $select.trigger('change');
    });
  }

  function updateCompartmentMediumNames() {
    let $nameInputs = $step4.find('.js-medium-section').find('.js-medium-name-input');
    let names = $.map($nameInputs.get(), function(input) { return $.trim($(input).val()) });

    $step4.find('.js-compartment-section .js-medium-names-select').each(function() {
      let $nameSelect = $(this);
      let options = $nameSelect.find('option').get();

      for (let [index, name] of Object.entries(names)) {
        if (index < options.length) {
          $(options[index]).html(name);
        } else {
          $nameSelect.append(`<option>${name}</option>`);
        }
      }
    });
  }

  updateCompartmentMediumNames();
});
