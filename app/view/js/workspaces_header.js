Page('.workspaces-header-component', function($component) {
  $component.on('change', '.js-workspace-select', function(e) {
    let $option = $(e.currentTarget).find('option:selected');
    let url = $option.data('url');
    if (url) window.location = url;
  });

  $component.on('click', '.js-toggle-published', function(e) {
    e.preventDefault();

    let $button = $(e.currentTarget);
    let url     = $button.data('url');

    $.ajax({
      url: url,
      dataType: 'json',
      method: 'POST',
      success: function(response) {
        window.location.reload();
      },
    })
  });
});
