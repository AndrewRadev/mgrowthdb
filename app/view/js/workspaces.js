Page('.workspaces-page', function($page) {
  let $uploadContainer = $page.find('.js-upload-container');
  $uploadContainer.customFileInput();
  let $fileInput = $('.js-upload-container input[type=file]');

  let $submitButton = $page.find('input[type=submit]');

  $page.on('change', 'input[type=file]', updateDataPreview)

  let $includeErrorCheckbox = $page.find('input[name=includeError]');
  updatePreviewErrorColumns();
  $page.on('change', 'input[name=includeError]', updateDataPreview)

  updateUnitSelects($uploadContainer.parents('form'));
  $page.on('change', '.js-subject-type', (e) => updateUnitSelects($(e.currentTarget).parents('form')));

  $page.on('change', '.js-workspace-select', function(e) {
    let $option = $(e.currentTarget).find('option:selected');
    let url = $option.data('url');
    if (url) window.location = url;
  });

  $page.on('click', '.js-edit', function(e) {
    let $link = $(e.currentTarget);
    let $entry = $link.parents('.js-workspace-entry');

    let $viewContainer = $entry.find('.js-view-container');
    let $formContainer = $entry.find('.js-form-container');

    if ($viewContainer.is(':visible')) {
      $viewContainer.addClass('hidden');
      $formContainer.removeClass('hidden');
    } else {
      $viewContainer.removeClass('hidden');
      $formContainer.addClass('hidden');
    }
  });

  $page.on('submit', '.js-edit-form', function(e) {
    e.preventDefault();

    let $form = $(this);
    let $entry = $form.parents('.js-workspace-entry');

    $form.ajaxSubmit({
      success: function(response) {
        $entry.html(response);
      }
    });
  });

  $page.on('click', '.js-delete', function(e) {
    e.preventDefault();

    if (!confirm("Are you sure you want to delete this uploaded data?")) {
      return;
    }

    let $link = $(e.currentTarget);
    let $entry = $link.parents('.js-workspace-entry');
    let entryId = $entry.data('id');
    let deleteUrl = $link.attr('href');

    $.ajax({
      type: 'POST',
      url: deleteUrl,
      cache: false,
      success: function(response) {
        $entry.fadeOut(500);
      }
    })
  });

  $page.on('click', '.js-delete-all', function(e) {
    e.preventDefault();

    if (!confirm("Are you sure you want to delete all the data in this workspace?")) {
      return;
    }

    let $link = $(e.currentTarget);
    let deleteUrl = $link.attr('href');

    $.ajax({
      type: 'POST',
      url: deleteUrl,
      cache: false,
      success: function(response) {
        window.location.reload();
      }
    })
  });

  $page.on('click', '.js-delete-workspace', function(e) {
    e.preventDefault();

    if (!confirm("Are you sure you want to delete this workspace and all the uploaded data in it?")) {
      return;
    }

    let $link = $(e.currentTarget);
    let deleteUrl = $link.attr('href');

    $.ajax({
      type: 'POST',
      url: deleteUrl,
      cache: false,
      dataType: 'html',
      success: function(response) {
        window.location = response.url;
      }
    })
  });

  function updateUnitSelects($form) {
    let $subjectTypeSelect = $form.find('.js-subject-type');
    let subjectType = $subjectTypeSelect.val();

    let $noUnits         = $form.find('.js-no-units').addClass('hidden');
    let $growthUnits     = $form.find('.js-growth-units').addClass('hidden');
    let $metaboliteUnits = $form.find('.js-metabolite-units').addClass('hidden');

    if (subjectType == 'community' || subjectType == 'strain') {
      $growthUnits.removeClass('hidden');
    } else if (subjectType == 'metabolite') {
      $metaboliteUnits.removeClass('hidden');
    } else {
      $noUnits.removeClass('hidden');
    }
  }

  function updatePreviewErrorColumns() {
    let $errorCols = $page.find('.js-preview .js-error-column');

    if ($includeErrorCheckbox.is(':checked')) {
      $errorCols.removeClass('hidden');
    } else {
      $errorCols.addClass('hidden');
    }
  }

  function updateDataPreview() {
    let previewUrl = $uploadContainer.data('previewUrl')
    let formData   = new FormData();
    let file       = $fileInput[0].files[0];
    let $preview   = $page.find('.js-preview');

    if (!file) {
      updatePreviewErrorColumns();
      return;
    }

    formData.append("file", file, file.name);
    formData.append("includeError", $includeErrorCheckbox.is(':checked'));

    $preview.addClass('loading');

    $.ajax({
      type: 'POST',
      url: previewUrl,
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function(response) {
        $preview.html(response);
        $preview.removeClass('loading');
      }
    })
  }
})
