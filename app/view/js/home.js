Page('.homepage', function($page) {
  for (let i of [1, 2, 3]) {
    $page.on('click', `.js-example-${i} button,img.js-example-${i}`, function(e) {
      for (let j of [1, 2, 3]) {
        let $nonTarget = $page.find(`.js-example-${j}`);
        $nonTarget.removeClass('focus');
        $nonTarget.find('button').removeClass('green-button').addClass('white-button');
      }

      let $target = $page.find(`.js-example-${i}`);
      $target.addClass('focus');
      $target.find('button').removeClass('white-button').addClass('green-button');
    });
  }
});
