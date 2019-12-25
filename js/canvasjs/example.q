/default is line chart
lineData: ([] ts: 2019.01.01D00:00 + 1D * til 10; price: 10000 + 10?100)
/multiple series - 1 column per series
multilineData: ([] ts: 2019.01.01D00:00 + 1D * til 10; price: 10?100; price2: 10?200)
/change to column chart if first column type is symbol
colData: ([] sym: `a`b`c`d`e`f`g`h`i`j`k`l; volume: 12#100 200 300)
/you can also have multiple series for column chart
multicolData: ([] sym: `a`b`c`d`e`f`g`h`i`j`k`l; volume: 12#100 200 300; volume2: 12#400 330 210)
/use candlestick automatically if column name contains open, high, low, close. with optional volume column
ohlcvData: ([] date: 2019.01.01 + til 5; high: 105 99 150 120 180; low: 99 84 110 110 150; close: 102 99 105 120 180; open: 100 90 110 120 140; volume: 10000 15000 9000 12000 11000)
/multiple series - if second column type is symbol
multiSymData: ([] date: 6#(2019.01.01 + til 3); sym: raze 3#'`a`b; price: 100 + 6?100)
multiSymData: ([] date: 6#(2019.01.01 + til 3); sym: raze 3#'`a`b; price: 100 + 6?100; price2: 100 + 6?100)
/auto generate 2nd axis if range is more than 50 times different 
needAxis2Data: ([] time: "z"$2019.01.01 + til 3; a: 3?100; b: 3?1000; c: 3?100; d: 3?100000)
/can also plot list or dict directly
10?100
(`a`b`c)!(100; 120; 130)

/override option by adding chart hints
/s - change type to scatter by prefixing s: to column name
`ts`s:a`s:b xcol pointData: ([] ts: 100 * til 3; a: 3?100; b: 3?1000)
/y2 - specify 2nd axis by prefixing y2: to column name
`time`a`y2:b xcol ([] time: 2019.01.01 + til 3; a: 3?100; b: 3?1000)
/bu - bubble chart will use next column as bubble size
`time`bu:a xcol ([] time: 2019.01.01 + til 3; a: 3?100; b: 3?1000)

/other options
/see file chart/canvasjs.q method .st.chart.chartTypeHints
/see https://canvasjs.com/docs/charts/chart-types/
/ `s`scatter!2#`scatter;
/ `b`ba`bar!3#`bar;
/ `bu`bubble!2#`bubble;
/ `c`col`column!3#`column;
/ `a`area!2#`area;
/ `sa`stackedArea!2#`stackedArea;
/ `a100`area100!2#`stackedArea100;
/ `p`pie!2#`pie;
/ `sc`stackedColumn!2#`stackedColumn;
/ `sc100`stackedColumn100!2#`stackedColumn100;
/ `sb`stackedBar!2#`stackedBar;
/ `sb100`stackedBar100!2#`stackedBar100;
/ `w`waterfall!2#`waterfall;