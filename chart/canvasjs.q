.st.collapseOhlc: {c: `open`high`low`close; $[all c in cols x; c _ update ohlc: flip x[c] from x; x]};
.st.unjoin: {#[;x] each {x[0] ,/: 1 _ x} cols x};
.st.colDataType: {type (value flip y)[x]};
.st.pxcol: {(`$(string[x], "_"),/: string cols y) xcol y};
.st.unmelt: {
  if[not 11h=.st.colDataType[1; x];: enlist x];
  t: {?[x; (); (enlist y[1])!enlist y[1]; {x!x} y _ 1]}[x] cols x;
  {.st.pxcol[y] flip x[y]}[t] each raze value flip key t};
.st.prepData: {raze .st.unjoin each .st.unmelt .st.collapseOhlc x};

.st.d: {(enlist x)!enlist y};
.st.guessType: {
  c: string (cols x[0])[1];
  $[
    c like "*column_*"; `column;
    c like "*bar_*"; `bar;
    c like "*scatter_*"; `scatter;
    c like "*point_*"; `scatter;
    c like "*stack_*"; `stackedColumn;
    c like "*stack100_*"; `stackedColumn100;
    c like "*area_*"; `stackedArea;
    c like "*area100_*"; `stackedArea100;
    c like "*pie_*"; `pie;
    c like "*waterfall_*"; `waterfall;
    c like "*volume*"; `column;
    0h =.st.colDataType[1; x]; `candlestick; /ohlc data comes as list
    11h=.st.colDataType[0; x]; `column; /x data is symbol
    `line]};

.st.chartOptions: raze (.st.d[`zoomEnabled; 1b]; .st.d[`axisX; .st.d[`labelAngle; -30]]; .st.d[`axisY; .st.d[`includeZero; 0b]]; .st.d[`toolTip; .st.d[`content; "{x}<br/><span style='\"'color: {color};'\"'>{name}</span>: <strong>{y}</strong>"]]);
.st.buildChart: {
  series: .st.prepData 0!x;
  types: .st.guessType each series;
  names: {(key flip x) 1} each series;
  axisYTypes: (`primary; `secondary){not x=first x} 50 < {max[x]%x} max each {max raze 1 _ flip x} each series;
  dataPoints: {$[11h=.st.colDataType[0] x;`label`y; `x`y] xcol x} each series;
  data: `type xcol update showInLegend: 1b from ([] typ: types; name: names; axisYType: axisYTypes; dataPoints: dataPoints);
  .st.chartOptions, .st.d[`data] data};