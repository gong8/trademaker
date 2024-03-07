export function getNewOptions(data: any) {
  let newDataPoints = [];
  if (data) {
    for (const dict of data.results) {
      // [Open, High, Low, Close]
      const {
        o: open, c: close,
        h: high, l: low,
      } = dict;
      const time = new Date(dict.t);
      const point = {x: time, y: [open, high, low, close]};
      newDataPoints.push(point);
    }
  }
  return ({
    theme: "dark2",
    backgroundColor: "#000000",
    title: {
      text: ""
    },
    data: [{
      type: "candlestick",
      xValueFormatString: "MMM YYYY",
      yValueFormatString: "#,##0.00",
      dataPoints: newDataPoints,
    }]
  });
}