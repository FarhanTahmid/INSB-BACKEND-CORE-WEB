/*
Template Name: Symox - Admin & Dashboard Template
Author: Themesbrand
Website: https://themesbrand.com/
Contact: themesbrand@gmail.com
File: Apexchart init js
*/

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

//  Line chart datalabel
var barchartColors = getChartColorsArray("line_chart_datalabel");
var options = {
    chart: {
      height: 380,
      type: 'line',
      zoom: {
        enabled: false
      },
      toolbar: {
        show: false
      }
    },
    colors: barchartColors,
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: [3, 3],
      curve: 'straight'
    },
    series: [{
      name: "High - 2018",
      data: [26, 24, 32, 36, 33, 31, 33]
    },
    {
      name: "Low - 2018",
      data: [14, 11, 16, 12, 17, 13, 12]
    }
    ],
    title: {
      text: 'Average High & Low Temperature',
      align: 'left',
      style: {
        fontWeight: 500,
      },
    },
    grid: {
      row: {
        colors: ['transparent', 'transparent'], // takes an array which will be repeated on columns
        opacity: 0.2
      },
      borderColor: '#f1f1f1'
    },
    markers: {
      style: 'inverted',
      size: 6
    },
    xaxis: {
      categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
      title: {
        text: 'Month'
      }
    },
    yaxis: {
      title: {
        text: 'Temperature'
      },
      min: 5,
      max: 40
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      floating: true,
      offsetY: -25,
      offsetX: -5
    },
    responsive: [{
      breakpoint: 600,
      options: {
        chart: {
          toolbar: {
            show: false
          }
        },
        legend: {
          show: false
        },
      }
    }]
  }
  
  var chart = new ApexCharts(
    document.querySelector("#line_chart_datalabel"),
    options
  );
  
  chart.render();
  
  
  //  Dashed line chart
  var barchartColors = getChartColorsArray("line_chart_dashed");
  var options = {
    chart: {
      height: 380,
      type: 'line',
      zoom: {
        enabled: false
      },
      toolbar: {
        show: false,
      }
    },
    colors: barchartColors,
    dataLabels: {
      enabled: false
    },
    stroke: {
      width: [3, 4, 3],
      curve: 'straight',
      dashArray: [0, 8, 5]
    },
    series: [{
      name: "Session Duration",
      data: [45, 52, 38, 24, 33, 26, 21, 20, 6, 8, 15, 10]
    },
    {
      name: "Page Views",
      data: [36, 42, 60, 42, 13, 18, 29, 37, 36, 51, 32, 35]
    },
    {
      name: 'Total Visits',
      data: [89, 56, 74, 98, 72, 38, 64, 46, 84, 58, 46, 49]
    }
    ],
    title: {
      text: 'Page Statistics',
      align: 'left',
      style: {
        fontWeight: 500,
      },
    },
    markers: {
      size: 0,
  
      hover: {
        sizeOffset: 6
      }
    },
    xaxis: {
      categories: ['01 Jan', '02 Jan', '03 Jan', '04 Jan', '05 Jan', '06 Jan', '07 Jan', '08 Jan', '09 Jan',
        '10 Jan', '11 Jan', '12 Jan'
      ],
    },
    tooltip: {
      y: [{
        title: {
          formatter: function (val) {
            return val + " (mins)"
          }
        }
      }, {
        title: {
          formatter: function (val) {
            return val + " per session"
          }
        }
      }, {
        title: {
          formatter: function (val) {
            return val;
          }
        }
      }]
    },
    grid: {
      borderColor: '#f1f1f1',
    }
  }
  
  var chart = new ApexCharts(
    document.querySelector("#line_chart_dashed"),
    options
  );
  
  chart.render();

  
// Basic area Charts
var barchartColors = getChartColorsArray("area_chart_basic");
var options = {
    series: [{
      name: "STOCK ABC",
      data: series.monthDataSeries1.prices
    }],
    chart: {
      type: 'area',
      height: 350,
      zoom: {
        enabled: false
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'straight'
    },
  
    title: {
      text: 'Fundamental Analysis of Stocks',
      align: 'left',
      style: {
        fontWeight: 500,
      },
    },
    subtitle: {
      text: 'Price Movements',
      align: 'left'
    },
    labels: series.monthDataSeries1.dates,
    xaxis: {
      type: 'datetime',
    },
    yaxis: {
      opposite: true
    },
    legend: {
      horizontalAlign: 'left'
    },
    colors: ["#038edc"]
  };
  
  var chart = new ApexCharts(document.querySelector("#area_chart_basic"), options);
  chart.render();
  
  
  //  Spline Area Charts
  var barchartColors = getChartColorsArray("area_chart_spline");
  var options = {
    series: [{
      name: 'series1',
      data: [31, 40, 28, 51, 42, 109, 100]
    }, {
      name: 'series2',
      data: [11, 32, 45, 32, 34, 52, 41]
    }],
    chart: {
      height: 350,
      type: 'area'
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth'
    },
    colors: barchartColors,
    xaxis: {
      type: 'datetime',
      categories: ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z", "2018-09-19T03:30:00.000Z", "2018-09-19T04:30:00.000Z", "2018-09-19T05:30:00.000Z", "2018-09-19T06:30:00.000Z"]
    },
    tooltip: {
      x: {
        format: 'dd/MM/yy HH:mm'
      },
    },
  };
  
  var chart = new ApexCharts(document.querySelector("#area_chart_spline"), options);
  chart.render();


  
// Basic Column Chart
var barchartColors = getChartColorsArray("column_chart");
var options = {
    chart: {
      height: 350,
      type: 'bar',
      toolbar: {
        show: false,
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '45%',
        endingShape: 'rounded'
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    series: [{
      name: 'Net Profit',
      data: [46, 57, 59, 54, 62, 58, 64, 60, 66]
    }, {
      name: 'Revenue',
      data: [74, 83, 102, 97, 86, 106, 93, 114, 94]
    }, {
      name: 'Free Cash Flow',
      data: [37, 42, 38, 26, 47, 50, 54, 55, 43]
    }],
    colors: barchartColors,
    xaxis: {
      categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    },
    yaxis: {
      title: {
        text: '$ (thousands)'
      }
    },
    grid: {
      borderColor: '#f1f1f1',
    },
    fill: {
      opacity: 1
  
    },
    tooltip: {
      y: {
        formatter: function (val) {
          return "$ " + val + " thousands"
        }
      }
    }
  }
  
  var chart = new ApexCharts(
    document.querySelector("#column_chart"),
    options
  );
  
  chart.render();
  
  
  // Column with Datalabels
  var barchartColors = getChartColorsArray("column_chart_datalabel");
  var options = {
    chart: {
      height: 350,
      type: 'bar',
      toolbar: {
        show: false,
      }
    },
    plotOptions: {
      bar: {
        dataLabels: {
          position: 'top', // top, center, bottom
        },
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val) {
        return val + "%";
      },
      offsetY: -20,
      style: {
        fontSize: '12px',
        colors: ["#adb5bd"]
      }
    },
    series: [{
      name: 'Inflation',
      data: [2.5, 3.2, 5.0, 10.1, 4.2, 3.8, 3, 2.4, 4.0, 1.2, 3.5, 0.8]
    }],
    colors: barchartColors,
    grid: {
      borderColor: '#f1f1f1',
    },
    xaxis: {
      categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
      position: 'top',
      labels: {
        offsetY: -18,
      },
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      },
      crosshairs: {
        fill: {
          type: 'gradient',
          gradient: {
            colorFrom: '#D8E3F0',
            colorTo: '#BED1E6',
            stops: [0, 100],
            opacityFrom: 0.4,
            opacityTo: 0.5,
          }
        }
      },
      tooltip: {
        enabled: true,
        offsetY: -35,
  
      }
    },
    fill: {
      gradient: {
        shade: 'light',
        type: "horizontal",
        shadeIntensity: 0.25,
        gradientToColors: undefined,
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [50, 0, 100, 100]
      },
    },
    yaxis: {
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false,
      },
      labels: {
        show: false,
        formatter: function (val) {
          return val + "%";
        }
      }
    },
    title: {
      text: 'Monthly Inflation in Argentina, 2002',
      floating: true,
      offsetY: 320,
      align: 'center',
      style: {
        color: '#444'
      },
      style: {
        fontWeight: 500,
      },
    },
  }
  
  var chart = new ApexCharts(
    document.querySelector("#column_chart_datalabel"),
    options
  );
  
  chart.render();

  
// Basic Bar chart
var barchartColors = getChartColorsArray("bar_chart");
var options = {
    chart: {
      height: 350,
      type: 'bar',
      toolbar: {
        show: false,
      }
    },
    plotOptions: {
      bar: {
        horizontal: true,
      }
    },
    dataLabels: {
      enabled: false
    },
    series: [{
      data: [380, 430, 450, 475, 550, 584, 780, 1100, 1220, 1365]
    }],
    colors: barchartColors,
    grid: {
      borderColor: '#f1f1f1',
    },
    xaxis: {
      categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan', 'United States', 'China', 'Germany'],
    }
  }
  
  var chart = new ApexCharts(
    document.querySelector("#bar_chart"),
    options
  );
  
  chart.render();
  
  // Custom DataLabels Bar
  var barchartColors = getChartColorsArray("custom_datalabels_bar");
  var options = {
    series: [{
      data: [400, 430, 448, 470, 540, 580, 690, 1100, 1200, 1380]
    }],
    chart: {
      type: 'bar',
      height: 350,
      toolbar: {
        show: false,
      }
    },
    plotOptions: {
      bar: {
        barHeight: '100%',
        distributed: true,
        horizontal: true,
        dataLabels: {
          position: 'bottom'
        },
      }
    },
    colors: barchartColors,
    colors: ['#5fd0f3', '#495057', '#e83e8c', '#13d8aa', '#f34e4e', '#2b908f', '#f9a3a4', '#564ab1',
      '#f1734f', '#038edc'],
    dataLabels: {
      enabled: true,
      textAnchor: 'start',
      style: {
        colors: ['#fff']
      },
      formatter: function (val, opt) {
        return opt.w.globals.labels[opt.dataPointIndex] + ":  " + val
      },
      offsetX: 0,
      dropShadow: {
        enabled: false
      }
    },
    stroke: {
      width: 1,
      colors: ['#fff']
    },
    xaxis: {
      categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan',
        'United States', 'China', 'India'],
    },
    yaxis: {
      labels: {
        show: false
      }
    },
    title: {
      text: 'Custom DataLabels',
      align: 'center',
      floating: true,
      style: {
        fontWeight: 600,
      },
    },
    subtitle: {
      text: 'Category Names as DataLabels inside bars',
      align: 'center',
    },
    tooltip: {
      theme: 'dark',
      x: {
        show: false
      },
      y: {
        title: {
          formatter: function () {
            return ''
          }
        }
      }
    }
  };
  
  var chart = new ApexCharts(document.querySelector("#custom_datalabels_bar"), options);
  chart.render();


  
// Mixed - Line Column Chart
var barchartColors = getChartColorsArray("line_column_chart");
var options = {
    series: [{
    name: 'Website Blog',
    type: 'column',
    data: [440, 505, 414, 671, 227, 413, 201, 352, 752, 320, 257, 160]
  }, {
    name: 'Social Media',
    type: 'line',
    data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16]
  }],
    chart: {
    height: 350,
    type: 'line',
    toolbar: {
      show: false,
    }
  },
  stroke: {
    width: [0, 4]
  },
  title: {
    text: 'Traffic Sources',
    style: {
      fontWeight: 600,
    },
  },
  dataLabels: {
    enabled: true,
    enabledOnSeries: [1]
  },
  labels: ['01 Jan 2001', '02 Jan 2001', '03 Jan 2001', '04 Jan 2001', '05 Jan 2001', '06 Jan 2001', '07 Jan 2001', '08 Jan 2001', '09 Jan 2001', '10 Jan 2001', '11 Jan 2001', '12 Jan 2001'],
  xaxis: {
    type: 'datetime'
  },
  yaxis: [{
    title: {
      text: 'Website Blog',
      style: {
        fontWeight: 600,
      },
    },
  
  }, {
    opposite: true,
    title: {
      text: 'Social Media',
      style: {
        fontWeight: 600,
      },
    }
  }],
  colors: barchartColors,
  };

  var chart = new ApexCharts(document.querySelector("#line_column_chart"), options);
  chart.render();

  // Multiple Y-Axis Charts
  var barchartColors = getChartColorsArray("multi_chart");
  var options = {
    series: [{
    name: 'Income',
    type: 'column',
    data: [1.4, 2, 2.5, 1.5, 2.5, 2.8, 3.8, 4.6]
  }, {
    name: 'Cashflow',
    type: 'column',
    data: [1.1, 3, 3.1, 4, 4.1, 4.9, 6.5, 8.5]
  }, {
    name: 'Revenue',
    type: 'line',
    data: [20, 29, 37, 36, 44, 45, 50, 58]
  }],
    chart: {
    height: 350,
    type: 'line',
    stacked: false,
    toolbar: {
      show: false,
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    width: [1, 1, 4]
  },
  title: {
    text: 'XYZ - Stock Analysis (2009 - 2016)',
    align: 'left',
    offsetX: 110,
    style: {
      fontWeight: 600,
    },
  },
  xaxis: {
    categories: [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
  },
  yaxis: [
    {
      axisTicks: {
        show: true,
      },
      axisBorder: {
        show: true,
        color: '#038edc'
      },
      labels: {
        style: {
          colors: '#038edc',
        }
      },
      title: {
        text: "Income (thousand crores)",
        style: {
          color: '#038edc',
          fontWeight: 600
        }
      },
      tooltip: {
        enabled: true
      }
    },
    {
      seriesName: 'Income',
      opposite: true,
      axisTicks: {
        show: true,
      },
      axisBorder: {
        show: true,
        color: '#038edc'
      },
      labels: {
        style: {
          colors: '#038edc',
        }
      },
      title: {
        text: "Operating Cashflow (thousand crores)",
        style: {
          color: '#038edc',
          fontWeight: 600
        }
      },
    },
    {
      seriesName: 'Revenue',
      opposite: true,
      axisTicks: {
        show: true,
      },
      axisBorder: {
        show: true,
        color: '#51d28c'
      },
      labels: {
        style: {
          colors: '#51d28c',
        },
      },
      title: {
        text: "Revenue (thousand crores)",
        style: {
          color: '#51d28c',
          fontWeight: 600
        }
      }
    },
  ],
  tooltip: {
    fixed: {
      enabled: true,
      position: 'topLeft', // topRight, topLeft, bottomRight, bottomLeft
      offsetY: 30,
      offsetX: 60
    },
  },
  legend: {
    horizontalAlign: 'left',
    offsetX: 40
  },
  colors: barchartColors,
  };

  var chart = new ApexCharts(document.querySelector("#multi_chart"), options);
  chart.render();


var barchartColors = getChartColorsArray("basic_timeline");
var options = {
    series: [
    {
      data: [
        {
          x: 'Code',
          y: [
            new Date('2019-03-02').getTime(),
            new Date('2019-03-04').getTime()
          ]
        },
        {
          x: 'Test',
          y: [
            new Date('2019-03-04').getTime(),
            new Date('2019-03-08').getTime()
          ]
        },
        {
          x: 'Validation',
          y: [
            new Date('2019-03-08').getTime(),
            new Date('2019-03-12').getTime()
          ]
        },
        {
          x: 'Deployment',
          y: [
            new Date('2019-03-12').getTime(),
            new Date('2019-03-18').getTime()
          ]
        }
      ]
    }
  ],
    chart: {
    height: 350,
    type: 'rangeBar',
    toolbar: {
      show: false,
    }
  },
  plotOptions: {
    bar: {
      horizontal: true
    }
  },
  xaxis: {
    type: 'datetime'
  },
  colors: barchartColors,
};

var chart = new ApexCharts(document.querySelector("#basic_timeline"), options);
chart.render();


// Different Color For Each Bar
var barchartColors = getChartColorsArray("color_timeline");
var options = {
    series: [
    {
      data: [
        {
          x: 'Analysis',
          y: [
            new Date('2019-02-27').getTime(),
            new Date('2019-03-04').getTime()
          ],
          fillColor: barchartColors[0]
        },
        {
          x: 'Design',
          y: [
            new Date('2019-03-04').getTime(),
            new Date('2019-03-08').getTime()
          ],
          fillColor: barchartColors[1]
        },
        {
          x: 'Coding',
          y: [
            new Date('2019-03-07').getTime(),
            new Date('2019-03-10').getTime()
          ],
          fillColor: barchartColors[2]
        },
        {
          x: 'Testing',
          y: [
            new Date('2019-03-08').getTime(),
            new Date('2019-03-12').getTime()
          ],
          fillColor: barchartColors[3]
        },
        {
          x: 'Deployment',
          y: [
            new Date('2019-03-12').getTime(),
            new Date('2019-03-17').getTime()
          ],
          fillColor: barchartColors[4]
        }
      ]
    }
  ],
    chart: {
    height: 330,
    type: 'rangeBar',
    toolbar: {
      show: false,
    }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      distributed: true,
      dataLabels: {
        hideOverflowingLabels: false
      }
    }
  },
  dataLabels: {
    enabled: true,
    formatter: function(val, opts) {
      var label = opts.w.globals.labels[opts.dataPointIndex]
      var a = moment(val[0])
      var b = moment(val[1])
      var diff = b.diff(a, 'days')
      return label + ': ' + diff + (diff > 1 ? ' days' : ' day')
    },
  },
  xaxis: {
    type: 'datetime'
  },
  yaxis: {
    show: true
  },

  };

  var chart = new ApexCharts(document.querySelector("#color_timeline"), options);
  chart.render();

  
// Bubble Charts Generate Data

function generateData(baseval, count, yrange) {
    var i = 0;
    var series = [];
    while (i < count) {
      var x = Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
      var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
      var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;
  
      series.push([x, y, z]);
      baseval += 86400000;
      i++;
    }
    return series;
  }
  
  // Simple Bubble
  var barchartColors = getChartColorsArray("simple_bubble");
  var options = {
      series: [{
      name: 'Bubble1',
      data: generateData(new Date('11 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Bubble2',
      data: generateData(new Date('12 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Bubble3',
      data: generateData(new Date('13 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Bubble4',
      data: generateData(new Date('14 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    }],
      chart: {
        height: 350,
        type: 'bubble',
        toolbar: {
          show: false,
        }
    },
    dataLabels: {
        enabled: false
    },
    fill: {
        opacity: 0.8
    },
    title: {
        text: 'Simple Bubble Chart',
        style: {
          fontWeight: 500,
        },
    },
    xaxis: {
        tickAmount: 12,
        type: 'category',
    },
    yaxis: {
        max: 70
    },
    colors: barchartColors,
    };
  
    var chart = new ApexCharts(document.querySelector("#simple_bubble"), options);
    chart.render();
  
    // 3D Bubble
    var barchartColors = getChartColorsArray("bubble_chart");
    var options = {
      series: [{
      name: 'Product1',
      data: generateData(new Date('11 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Product2',
      data: generateData(new Date('11 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Product3',
      data: generateData(new Date('11 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    },
    {
      name: 'Product4',
      data: generateData(new Date('11 Feb 2017 GMT').getTime(), 20, {
        min: 10,
        max: 60
      })
    }],
      chart: {
      height: 350,
      type: 'bubble',
      toolbar: {
        show: false,
      }
    },
    dataLabels: {
      enabled: false
    },
    fill: {
      type: 'gradient',
    },
    title: {
      text: '3D Bubble Chart',
      style: {
        fontWeight: 500,
      },
    },
    xaxis: {
      tickAmount: 12,
      type: 'datetime',
      labels: {
          rotate: 0,
      }
    },
    yaxis: {
      max: 70
    },
    theme: {
      palette: 'palette2'
    },
    colors: barchartColors,
    };
  
    var chart = new ApexCharts(document.querySelector("#bubble_chart"), options);
    chart.render();


    
//  Simple Pie Charts
var barchartColors = getChartColorsArray("simple_pie_chart");
var options = {
    series: [44, 55, 13, 43, 22],
    chart: {
      height: 350,
      type: 'pie',
    },
    labels: ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
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
  
  var chart = new ApexCharts(document.querySelector("#simple_pie_chart"), options);
  chart.render();
  
  
  // Simple Donut Charts
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

  
//  Radialbar Charts
var barchartColors = getChartColorsArray("basic_radialbar");
var options = {
    series: [70],
    chart: {
    height: 350,
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      hollow: {
        size: '70%',
      }
    },
  },
  labels: ['Cricket'],
  colors: barchartColors,
  };

  var chart = new ApexCharts(document.querySelector("#basic_radialbar"), options);
  chart.render();
 
  // Multi-Radial Bar
  var barchartColors = getChartColorsArray("multiple_radialbar");
  var options = {
    series: [44, 55, 67, 83],
    chart: {
    height: 350,
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      dataLabels: {
        name: {
          fontSize: '22px',
        },
        value: {
          fontSize: '16px',
        },
        total: {
          show: true,
          label: 'Total',
          formatter: function (w) {
            return 249
          }
        }
      }
    }
  },
  labels: ['Apples', 'Oranges', 'Bananas', 'Berries'],
  colors: barchartColors,
  };

  var chart = new ApexCharts(document.querySelector("#multiple_radialbar"), options);
  chart.render();

  
// Basic Radar Chart
var barchartColors = getChartColorsArray("basic_radar");
var options = {
    series: [{
    name: 'Series 1',
    data: [80, 50, 30, 40, 100, 20],
  }],
    chart: {
    height: 350,
    type: 'radar',
    toolbar: {
      show: false
    }
  },
  stroke: {
    colors: barchartColors,
  },
  xaxis: {
    categories: ['January', 'February', 'March', 'April', 'May', 'June']
  }
  };

  var chart = new ApexCharts(document.querySelector("#basic_radar"), options);
  chart.render();


  // Radar Chart - Multi series
  var barchartColors = getChartColorsArray("multi_radar");
  var options= {
    series: [ {
        name: 'Series 1',
        data: [80, 50, 30, 40, 100, 20],
    },
    {
        name: 'Series 2',
        data: [20, 30, 40, 80, 20, 80],
    },
    {
        name: 'Series 3',
        data: [44, 76, 78, 13, 43, 10],
    }
    ],
    chart: {
        height: 350,
        type: 'radar',
        dropShadow: {
            enabled: true, blur: 1, left: 1, top: 1
        },
        toolbar: {
            show: false
        },
    },
    stroke: {
        width: 2
    },
    fill: {
        opacity: 0.2
    },
    markers: {
        size: 0
    },
    colors: barchartColors,
    xaxis: {
        categories: ['2014', '2015', '2016', '2017', '2018', '2019']
    }
  };
  var chart=new ApexCharts(document.querySelector("#multi_radar"), options);
  chart.render();

  
// Basic Polar Area 
var barchartColors = getChartColorsArray("basic_polar_area");
var options = {
    series: [14, 23, 21, 17, 15, 10, 12, 17, 21],
    chart: {
    type: 'polarArea',
    width: 400,
  },
  labels: ['Series A', 'Series B', 'Series C', 'Series D', 'Series E', 'Series F', 'Series G', 'Series H', 'Series I'],
  stroke: {
    colors: ['#fff']
  },
  fill: {
    opacity: 0.8
  },
  
  legend: {
    position: 'bottom'
  },
  colors: barchartColors,
  };

  var chart = new ApexCharts(document.querySelector("#basic_polar_area"), options);
  chart.render();

  // Polar-Area Monochrome Charts

  var options = {
    series: [42, 47, 52, 58, 65],
    chart: {
    width: 400,
    type: 'polarArea'
  },
  labels: ['Rose A', 'Rose B', 'Rose C', 'Rose D', 'Rose E'],
  fill: {
    opacity: 1
  },
  stroke: {
    width: 1,
    colors: undefined
  },
  yaxis: {
    show: false
  },
  legend: {
    position: 'bottom'
  },
  plotOptions: {
    polarArea: {
      rings: {
        strokeWidth: 0
      },
      spokes: {
        strokeWidth: 0
      },
    }
  },
  theme: {
    mode: 'light', 
    palette: 'palette1',
    monochrome: {
      enabled: true,
      shadeTo: 'light',
      color: '#038edc',
      shadeIntensity: 0.6
    }
  }
  };

  var chart = new ApexCharts(document.querySelector("#monochrome_polar_area"), options);
  chart.render();
