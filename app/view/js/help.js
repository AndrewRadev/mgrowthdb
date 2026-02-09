Page('.help-page-index', function($page) {
  let $pageListContainer = $page.find('.js-page-list-container');
  let $searchInput = $('.js-search-input');

  if ($searchInput.val().trim().length > 0) {
    updatePage($searchInput);
  }

  $page.on('keyup', '.js-search-input', _.debounce(function() {
    let $searchInput = $(this);
    updatePage($searchInput);
  }, 200));

  function updatePage($searchInput) {
    let $form = $searchInput.parents('form');
    $searchInput.addClass('loading-input');

    $form.ajaxSubmit({
      success: function(response) {
        $pageListContainer.html(response);
        $searchInput.removeClass('loading-input');
      }
    });
  }
});

Page('.help-page', function($page) {
  renderMathInElement($page[0]);
});
