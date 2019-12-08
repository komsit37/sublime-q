.st.unjoin: {#[;x] each {x[0] ,/: 1 _ x} cols x};
.st.d: {(enlist x)!enlist y};
.st.unmelt: {
  c: cols x;
  t: ?[x; (); (enlist c[1])!enlist c[1]; {x!x} c _ 1];
  {t: flip x[y]; ({`$"_" sv string x} each y ,/: cols t) xcol t}[t] each raze value flip key t};
.st.needUnmelt: {"s"=(exec t from meta x)[1]};
.st.prepData: {raze .st.unjoin each {$[.st.needUnmelt[x]; .st.unmelt[x]; enlist x]} x};
.st.options: raze (.st.d[`zoomEnabled; 1b]; .st.d[`axisX; .st.d[`labelAngle; -30]]; .st.d[`axisY; .st.d[`includeZero; 0b]]; d[`toolTip; d[`content; "{x}<br/><span style='\"'color: {color};'\"'>{name}</span>: <strong>{y}</strong>"]]);
.st.columnDataSeries: {.st.d[`data] {.st.d[`type; `column], .st.d[`showInLegend; 1b], .st.d[`name; cols[x]1], .st.d[`dataPoints; `label`y xcol x]} each x};
.st.lineDataSeries: {.st.options, .st.d[`data] {.st.d[`type; `line], .st.d[`markerType; `none], .st.d[`showInLegend; 1b], .st.d[`name; cols[x]1], .st.d[`dataPoints; `x`y xcol x]} each x};
.st.pointDataSeries: {.st.options, .st.d[`data] {.st.d[`type; `scatter], .st.d[`showInLegend; 1b], .st.d[`name; cols[x]1], .st.d[`dataPoints; `x`y xcol x]} each x};
.st.bubbleDataSeries: {.st.d[`data] {.st.d[`type; `bubble], .st.d[`showInLegend; 1b], .st.d[`name; cols[x]1], .st.d[`dataPoints; `x`y`z xcol x]} each x};
.st.autoSecondaryAxis: {([] axisYType: (`primary; `secondary) {not x=first x} 100 < {max[x]%x}{max raze 1 _ flip x} each x)};
.st.candlestickDataSeries: {.st.d[`type; `candlestick], .st.d[`dataPoints; `x`y xcol .st.transformOhlc[x]], .st.optionalLegendFromSym[x]}';
.st.transformOhlc: {{flip (1#x), .st.d[`ohlc] flip value `open`high`low`close#1 _ x} flip x};
.st.optionalLegendFromSym: {$[`sym in cols x; .st.d[`showInLegend; 1b], .st.d[`name; first x`sym]; .st.d[`showInLegend; 0b], .st.d[`name; `]]};
.st.volumnDataSeries: {.st.d[`type; `column], .st.d[`showInLegend; 0b], .st.d[`name; `], .st.d[`dataPoints; `x`y xcol x]}';
.st.volumnOption: {$[`volume in cols first x; .st.d[`axisY2; .st.d[`labelFontSize; 8], .st.d[`maximum] (10*exec max volume from first x)]; ()]};
.st.ohlcDataSeries: {
  dataSeries: raze {$[`volume in cols x; update axisYType: `secondary from .st.volumnDataSeries enlist ((cols x)[0], `volume)#x; ()]} each x;
  .st.options, .st.volumnOption[x], .st.d[`data] dataSeries, update axisYType: `primary from .st.candlestickDataSeries x};
.st.xType: {(`number`sym`timeseries) 1 + signum -11h + type first flip x};
.st.isOhlc: {all (count cols x) > (cols x)?`open`high`low`close};
.st.guessChartType: {$[.st.isOhlc[x]; `ohlc; .st.xType[x]]};
.st.chartFn: (`ohlc`number`sym`timeseries)!(.st.ohlcDataSeries; .st.pointDataSeries; .st.columnDataSeries; .st.lineDataSeries);
.st.autoChart: {
  chartType: .st.guessChartType[x];
  $[`ohlc=chartType; .st.ohlcDataSeries enlist x; {t: y[x]; t[`data]: t[`data],'.st.autoSecondaryAxis[x]; t}[; .st.chartFn[chartType]] .st.prepData x]};