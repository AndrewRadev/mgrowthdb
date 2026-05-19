Page('.workspaces-page', function($page) {
  let $uploadContainer = $page.find('.js-upload-container');
  $uploadContainer.customFileInput();
  let $fileInput = $('.js-upload-container input[type=file]');

  let $submitButton = $page.find('input[type=submit]');

  $page.on('change', 'input[type=file]', updateDataPreview)

  let $includeErrorCheckbox = $page.find('input[name=includeError]');
  updatePreviewErrorColumns();
  $page.on('change', 'input[name=includeError]', updateDataPreview)

  updateUnitSelects();
  $page.on('change', '.js-subject-type', updateUnitSelects);

  function updateUnitSelects() {
    let $subjectTypeSelect = $page.find('.js-subject-type');
    let subjectType = $subjectTypeSelect.val();

    let $noUnits         = $page.find('.js-no-units').addClass('hidden');
    let $growthUnits     = $page.find('.js-growth-units').addClass('hidden');
    let $metaboliteUnits = $page.find('.js-metabolite-units').addClass('hidden');

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
