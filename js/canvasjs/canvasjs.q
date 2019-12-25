.st.chart.collapseOhlc: {c: `open`high`low`close; $[all c in cols x; c _ update ohlc: flip x[c] from x; x]};
.st.chart.unjoin: {#[;x] each {x[0] ,/: 1 _ x} cols x};
.st.chart.pxcol: {(`$(string[x], "_"),/: string cols y) xcol y};
.st.chart.colDataType: {type (value flip y)[x]};

.st.chart.extractHints: {l: `$":" vs' string cols x; c: (raze -1#'l); (`t`hints)!(c xcol x; c!-1 _' l)};

.st.chart.collapseBubble: {
  xt: x[`t]; xhints: x[`hints];
  bu: {`bu in x} each xhints;
  if[not any bu; :x];
  ycols: where bu; zcols: where prev bu;
  tt: ((ycols, zcols) _ xt) ,'  flip raze {(enlist y)!enlist flip x[y, z]}[xt]'[ycols; zcols];
  (`t`hints)!(tt; (cols tt)#xhints)};

.st.chart.unmelt: {
  if[not 11h=.st.chart.colDataType[1; x`t]; :flip enlist each x];
  mt: {?[x; (); (enlist y[1])!enlist y[1]; {x!x} y _ 1]}[x[`t]] cols x[`t];
  s: raze value flip key mt;
  tt: {flip x[y]}[mt] each s;
  newt: .st.chart.pxcol'[s; tt];
  newHints: {y!value x}[(cols first tt)#x[`hints]] each (cols each newt);
  flip (`t`hints)!(newt; newHints)};

.st.chart.prepData: {
  t: .st.chart.collapseOhlc x;
  t: .st.chart.extractHints t;
  t: .st.chart.collapseBubble[t];
  t: .st.chart.unmelt[t];
  t: select raze .st.chart.unjoin each t, raze .st.chart.unjoin each hints from t;
  t};

.st.chart.chartTypeHints: {
  r : `s`scatter!2#`scatter;
  r,: `b`ba`bar!3#`bar;
  r,: `bu`bubble!2#`bubble;
  r,: `c`col`column!3#`column;
  r,: `a`area!2#`area;
  r,: `sa`stackedArea!2#`stackedArea;
  r,: `a100`area100!2#`stackedArea100;
  r,: `p`pie!2#`pie;
  r,: `sc`stackedColumn!2#`stackedColumn;
  r,: `sc100`stackedColumn100!2#`stackedColumn100;
  r,: `sb`stackedBar!2#`stackedBar;
  r,: `sb100`stackedBar100!2#`stackedBar100;
  r,: `w`waterfall!2#`waterfall;
  r}[];

.st.chart.guessType: {[t; hints]
  $[
    not `=h:first raze value .st.chart.chartTypeHints hints; h;
    (string (cols t[0])[1]) like "*volume*"; `column;
    (0h =.st.chart.colDataType[1; t])&4=count first (value flip t)[1]; `candlestick; /ohlc data comes as list of 4
    (0h =.st.chart.colDataType[1; t])&2=count first (value flip t)[1]; `bubble; /bubble data comes as list of 2
    11h=.st.chart.colDataType[0; t]; `column; /x data is symbol
    `line]};

.st.chart.xyz: {
  v: value flip x;
  r: (enlist $[11h=type v[0]; `label; `x])! enlist v[0];
  r,:$[(0h=type v[1])&(2=count first v[1]);
    (`y`z)!flip v[1];
    (enlist `y)!enlist v[1]];
  flip r};

.st.chart.axisYType: {[t; hints]
  axisHints: {$[`y1 in x; `primary; `y2 in x; `secondary; `auto]} each hints;
  autoIndex: where axisHints=`auto;
  auto: (`primary; `secondary){not x=first x} 50 < {max[x]%x} max each {max raze 1 _ flip x} each t;
  @[axisHints; autoIndex; :; auto autoIndex]};

.st.chart.listOrDictToTable: {$[
  (type x) within (0h; 19h); {flip (`x`y)!(1 + til count x; x)} x; 
  99h=type x; {flip (`x`y)!(key x; value x)} x;
  x]};
.st.chart.adjustData: {
  if[(1=count x) and `column=first x[`type]; x: update color: `$"#4f81bc" from x]; /optionally adjust color for single column chart
  x};
.st.chart.chartOptions: {d: {(enlist x)!enlist y}; raze (d[`zoomEnabled; 1b]; d[`axisX; d[`labelAngle; -30]]; d[`axisY; d[`includeZero; 0b]]; d[`toolTip; d[`content; "{x}<br/><span style='\"'color: {color};'\"'>{name}</span>: <strong>{y}</strong><br/>{z}"]])}[];
.st.chart.buildChart: {
  t: .st.chart.listOrDictToTable x;
  series: .st.chart.prepData 0!t;
  types: .st.chart.guessType'[series[`t]; series[`hints]];
  names: {(key flip x) 1} each series[`t];
  axisYTypes: .st.chart.axisYType[series[`t]; series[`hints]];
  dataPoints: .st.chart.xyz each series[`t];
  markerTypes: (`circle`none) `line = types;
  data: `type xcol update showInLegend: 1b from ([] typ: types; markerType: markerTypes; name: names; axisYType: axisYTypes; dataPoints: dataPoints);
  data: .st.chart.adjustData[data];
  .st.chart.chartOptions, (enlist `data)! enlist data};