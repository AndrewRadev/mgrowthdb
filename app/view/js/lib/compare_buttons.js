// This function attaches events to "compare" and "uncompare" buttons on the
// given page container. These require buttons with specific classes to be
// present on the page.
//
// The global `document` is accessed to get the currently stored ids to compare
// and to update the sidebar UI.
//
function initCompareButtons($page) {
  let $compareData = $(document).find('[data-compare-context-ids]');

  let compareContextIds = new Set(getDataIds($compareData, 'compareContextIds'));
  let compareModelIds   = new Set(getDataIds($compareData, 'compareModelIds'));

  let studyId = $page.data('studyId');

  $page.find('.js-compare-container').each(function() {
    let $container = $(this);
    let contextIds = new Set(getDataIds($container, 'contextIds'));
    let modelIds   = new Set(getDataIds($container, 'modelIds'));

    if (
      (contextIds.size > 0 && contextIds.isSubsetOf(compareContextIds)) ||
      (modelIds.size > 0 && modelIds.isSubsetOf(compareModelIds))
    ) {
      $container.find('.js-uncompare').removeClass('hidden');
      $container.find('.js-compare').addClass('hidden');
    }
  });

  $page.on('click', '.js-compare a', function(e) {
    e.preventDefault();

    let $button    = $(this);
    let $wrapper   = $button.parents('.js-compare');
    let $container = $button.parents('.js-compare-container');

    let contextIds = getDataIds($container, 'contextIds');
    let modelIds   = getDataIds($container, 'modelIds');

    updateCompareData('add', contextIds, modelIds, function(compareData) {
      // Hide "compare" button, show "uncompare" button
      $wrapper.addClass('hidden');
      $container.find('.js-uncompare').removeClass('hidden');
    });
  });

  $page.on('click', '.js-uncompare a', function(e) {
    e.preventDefault();

    let $button    = $(this);
    let $wrapper   = $button.parents('.js-uncompare');
    let $container = $button.parents('.js-compare-container');

    let contextIds = getDataIds($container, 'contextIds');
    let modelIds   = getDataIds($container, 'modelIds');

    updateCompareData('remove', contextIds, modelIds, function(compareData) {
      // Hide "uncompare" section, show "compare" button
      $wrapper.addClass('hidden');
      $container.find('.js-compare').removeClass('hidden');

      // Unhighlight previously compared row
      $container.parents('.js-table-row').removeClass('highlight');
    });
  });
}

// This function makes an ajax request to update the "compare data" stored in
// the session.
//
function updateCompareData(action, contexts, models, successCallback) {
  $.ajax({
    type: 'POST',
    url: `/comparison/update/${action}.json`,
    data: JSON.stringify({'contexts': contexts, 'models': models}),
    cache: false,
    contentType: 'application/json',
    processData: true,
    success: function(response) {
      let compareData = JSON.parse(response);
      let recordCount = compareData.contextCount + compareData.modelCount;

      if (recordCount > 0) {
        countText = `(${compareData.contextCount + compareData.modelCount})`;
      } else {
        countText = '';
      }

      let $sidebarCompareItem = $(document).find('.js-sidebar-compare');
      $sidebarCompareItem.find('.js-count').html(countText);
      $sidebarCompareItem.animateClass('highlight', 500);

      successCallback(compareData)
    },
  })
}

function getDataIds($element, key) {
  let data = $element.data(key);
  if (!data) {
    return [];
  }

  return data.toString().split(',');
}
