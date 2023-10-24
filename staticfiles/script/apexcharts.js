  // Simple Donut Charts
  function getChartColorsArray(chartId) {
    if (document.getElementById(chartId) !== null) {
        var colors = document.getElementById(chartId).getAttribute("data-colors");
        colors = JSON.parse(colors);
        return colors.map(function (value) {
            var newValue = value.replace(" ", "");
            if (newValue.indexOf("--") != -1) {
                var color = getComputedStyle(document.documentElement).getPropertyValue(
                    newValue
                );
                if (color) return color;
            } else {
                return newValue;
            }
        });
    }
  }
  
  var barchartColors = getChartColorsArray("simple_dount_chart");
  var options = {
    series: [44, 55, 41, 17, 15],
    chart: {
      height: 350,
      type: 'donut',
    },
    legend: {
      position: 'bottom'
    },
    dataLabels: {
      dropShadow: {
        enabled: false,
      }
    },
    colors: barchartColors,
  };
  
  var chart = new ApexCharts(document.querySelector("#simple_dount_chart"), options);
  chart.render();

