// Traces that have continuous error bands need special handling, so we
// reimplement the "legend click" and "legend double click" events ourselves to
// enable the special behaviour.
//
// References:
// - https://plotly.com/javascript/plotlyjs-events/
// - https://plotly.com/python/continuous-error-bars/
//
function initPlotEvents(plotDiv) {
  plotDiv.on('plotly_legendclick', function(event) {
    let [targetCurves, newVisible] = getPlotVisibilityState(event);
    let update = {'visible': newVisible}

    Plotly.restyle(plotDiv, update, targetCurves);
    return false;
  });

  plotDiv.on('plotly_legenddoubleclick', function(event) {
    let [targetCurves, _] = getPlotVisibilityState(event);
    let visibility = [];

    for (let i of event.data.keys()) {
      if (targetCurves.indexOf(i) >= 0) {
        visibility.push(true);
      } else {
        visibility.push('legendonly');
      }
    }

    Plotly.restyle(plotDiv, {'visible': visibility});
    return false;
  });
}

// Returns [<clicked indices>, <new visibility state>]
function getPlotVisibilityState(clickEvent) {
  let clickedCurveIndex = clickEvent.curveNumber;
  let clickedCurve = clickEvent.data[clickedCurveIndex];

  let targetCurves = [clickedCurveIndex];

  let newVisible;
  if (typeof(clickedCurve.visible) == 'undefined') {
    // On initial load, the curve is not explicitly marked
    newVisible = 'legendonly';
  } else if (clickedCurve.visible == 'legendonly') {
    // It was hidden from view, so we show it:
    newVisible = true;
  } else {
    newVisible = 'legendonly';
  }

  for (let [i, curve] of clickEvent.data.entries()) {
    if (
      curve.name == `${clickedCurve.name} lower bound` ||
      curve.name == `${clickedCurve.name} upper bound`) {
      targetCurves.push(i);
    }
  }

  return [targetCurves, newVisible];
}
