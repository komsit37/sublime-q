//time or timespan
var timeReg = /^(\d*)D?(\d\d):(\d\d):?(\d\d)?.?(\d\d\d)?/;
//datetime or timestamp
var timestampReg = /^(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d.\d+)/;
//date
var dateReg = /^(\d\d\d\d-\d\d-\d\d)$/;

function parseTime(x, y) {
  var time = (y) ? y : new Date(0);
  var parts = timeReg.exec(x);
  if (!parts) return null;
  //console.log(parts);
  //0D
  if (parts[1] != "") time.setDate(time.getDate() + parseInt(parts[1]));
  //hours
  if (parts[2]) time.setHours(parseInt(parts[2]));
  //minutes
  if (parts[3]) time.setMinutes(parseInt(parts[3]));
  //seconds
  if (parts[4]) time.setSeconds(parseInt(parts[4]));
  //millis
  if (parts[5]) time.setMilliseconds(parseInt(parts[5]));
  return time;
};

//not used
// function parseTimestamp(x) {
//   var parts = timestampReg.exec(x);
//   if (!parts) return null;
//   var datetime = (parts[1]) ? new Date(parts[1]) : new Date();
//   if (parts[2]) datetime = parseTime(parts[2], datetime);
//   return datetime;
// };

function guessDataType(x){
  //console.log(x);
  if (dateReg.test(x)){
    return function(x){
      var p = x.split("-");
      return new Date(p[0], p[1], p[2]);
    };
  } else if (timeReg.test(x)){
    return parseTime;
  } else if (timestampReg.test(x)){
    return function(x){return new Date(x)};
  } else {
    return null;
  }
};

//check the first x, to see if it needs conversion
function formatCanvasJsData(data){
  if (data.length > 0 && data[0].dataPoints.length > 0) {
    var fn = guessDataType(data[0].dataPoints[0].x);
    if (fn) {
      data.forEach(x => x.dataPoints.forEach(x => x.x = fn(x.x)));
    }
  }
  return data;
};