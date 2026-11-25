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
            updateCompartmentMediumNames();
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
          let $container = $componentForm.parents('.js-medium-component-subform-list').first()
          $container.scrollTo($componentForm, 300);

          // Remove "box" class since it looks a bit crowded
          $componentForm.removeClass('box');
        }
      });
    },

    onDuplicate: function($newForm) {
      // Reset name
      $newForm.find('input[name$="name"]').val('');
      $newForm.find('.js-title').html('[New]')
    },

    beforeRemove: function($subform) {
      let $nameInput = $subform.find('input[name$="name"]');
      let removedName = $.trim($nameInput.val());

      // Remove options with this name from compartment inputs. In case there
      // are duplicates pre-validation, we only remove the first encounter
      $step4.find('.js-compartment-section .js-medium-names-select').each(function() {
        let nameOptions = $(this).find('option').get();

        for (let option of nameOptions) {
          let $option = $(option);

          if ($.trim($option.val()) === removedName) {
            $option.remove();
            break;
          }
        }
      });
    }
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

    afterAdd: function() {
      updateCompartmentMediumNames();
    }
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
      let selectedName = $nameSelect.parents('label').data('selected');

      for (let [index, name] of Object.entries(names)) {
        let isSelected = false;
        if (name === selectedName) {
          isSelected = true;
        }

        if (index < options.length) {
          let $option = $(options[index]);
          $option.html(name);
          if (isSelected) {
            $option.prop('selected', true)
          }
        } else {
          $nameSelect.append(`<option ${isSelected ? "selected": ""}>${name}</option>`);
        }
      }
    });
  }

  updateCompartmentMediumNames();
});
