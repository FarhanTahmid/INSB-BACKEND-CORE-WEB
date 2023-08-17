
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

// Function to fetch data from Django API
async function fetchData() {
  try {
    var x='{{session.session.id}}';
    console.log(x)
    x=Integer.parseInt(x)
    const response = await fetch('/recruitment/getPaymentStats/?session_id=' + encodeURIComponent(x));
    const data = await response.json();
    console.log(data)
    return data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error; // Rethrow the error for further handling
  }
}

// ... (getChartColorsArray and fetchData functions remain unchanged)

async function initializeDougnutChart() {
  try {
    var isdoughnutchart = document.getElementById('doughnut');
    var data = await fetchData(); // Fetch data from the Django API
    var doughnutChartColors = getChartColorsArray('doughnut');
    
    var doughnutChart = new Chart(isdoughnutchart, {
      type: 'doughnut',
      data: {
        labels: data.labels, // Use the fetched labels
        datasets: [
          {
            data: data.values, // Use the fetched data values
            backgroundColor: doughnutChartColors,
            hoverBackgroundColor: doughnutChartColors,
            hoverBorderColor: "#fff"
          }
        ]
      }
    });
  } catch (error) {
    console.error('Error initializing chart:', error);
  }
}

initializeDougnutChart();
