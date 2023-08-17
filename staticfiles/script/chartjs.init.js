/*
Template Name: Symox - Admin & Dashboard Template
Author: Themesbrand
Website: https://themesbrand.com/
Contact: themesbrand@gmail.com
File: chartjs init js
*/


// get colors array from the string
function getChartColorsArray(chartId) {
    if (document.getElementById(chartId) !== null) {
      var colors = document.getElementById(chartId).getAttribute("data-colors");
      var colors = JSON.parse(colors);
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


var isdoughnutchart = document.getElementById('doughnut');
doughnutChartColors =  getChartColorsArray('doughnut');
var lineChart = new Chart(isdoughnutchart, {
    type: 'doughnut',
    data: {
        labels: [
            "Desktops",
            "Tablets"
        ],
        datasets: [
            {
                data: [300, 210],
                backgroundColor: doughnutChartColors,
                hoverBackgroundColor: doughnutChartColors,
                hoverBorderColor: "#fff"
            }]
    }
});

