$.fn.animateClass = function(className, timeout) {
  let $this = $(this);

  $this.addClass(className);
  setTimeout(function() {
    $this.removeClass(className);
  }, timeout);

  return $this;
}

$.fn.animateVal = function(value) {
  $(this).val(value).animateClass('highlight', 500);
}
