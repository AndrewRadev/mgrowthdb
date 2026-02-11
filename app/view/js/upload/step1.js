Page('.upload-page .step-content.step-1.active', function($step1) {
  let $form = $step1.find('form');

  $step1.on('change', '.js-project-select', function() { updateProjectFields(); });
  $step1.on('change', '.js-study-select', function() { updateStudyFields(); });

  $step1.on('click', '.js-fetch-authors', function() {
    let $button = $(this);
    let $url = $step1.find('input[name=study_url]');
    let doi = ($url.val() || '').trim();

    if (!/^https\?:\/\//.test(doi)) {
      $url.val(`https://doi.org/${doi}`);
    }

    let $authorsInput      = $step1.find('input[name=authors]');
    let $authorsCacheInput = $step1.find('input[name=authorsCache]');

    let $authors   = $step1.find('.js-authors');
    let $studyName = $step1.find('input[name=study_name]');

    $button.prop('disabled', true);
    $url.addClass('loading-input');

    $.ajax({
      url: '/upload/fetch-authors/',
      method: 'POST',
      dataType: 'json',
      data: {'doi': doi},
      success: function(response) {
        $button.prop('disabled', false);
        $url.removeClass('loading-input');

        $authors.html(response.authorsHtml);

        $authorsInput.val(JSON.stringify(response.authors));
        $authorsCacheInput.val(response.authorCache);

        let existingStudyName = ($studyName.val() || '').trim();
        if (existingStudyName.length == 0 && response.studyName.length > 0) {
          $studyName.val(response.studyName);
        }
      }
    });
  });

  function updateProjectFields() {
    let $select = $form.find('.js-project-select');
    let $option = $select.find('option:selected');

    let $name        = $form.find('input[name=project_name]');
    let $description = $form.find('textarea[name=project_description]');

    if ($option.val() == '_new') {
      $name.val('');
      $description.val('');
    } else {
      $name.val($option.data('name'));
      $description.val($option.data('description'));
    }

    // If the selected study is not in this project, reset the study form
    if ($option.val() != '_new') {
      let selectedStudyUuid = $form.find('.js-study-select option:selected').val();
      let projectStudies = $option.data('studyUuids');

      if (!projectStudies.includes(selectedStudyUuid)) {
        $form.find('.js-study-select').val('_new').trigger('change');
      }
    }
  }

  function updateStudyFields() {
    let $select = $form.find('.js-study-select');
    let $option = $select.find('option:selected');

    let $name        = $form.find('input[name=study_name]');
    let $description = $form.find('textarea[name=study_description]');

    if ($option.val() == '_new') {
      $name.val('');
      $description.val('');
    } else {
      $name.val($option.data('name'));
      $description.val($option.data('description'));
    }

    // If the selected project is not the parent of this study, find it in the project form
    if ($option.val() != '_new') {
      let selectedProjectUuid = $form.find('.js-project-select option:selected').val();
      let projectUuid = $option.data('projectUuid');

      if (projectUuid != selectedProjectUuid) {
        $form.find('.js-project-select').val(projectUuid).trigger('change');
      }
    }
  }
});
