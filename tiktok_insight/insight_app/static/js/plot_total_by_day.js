Chart.defaults.color = "white";
Chart.defaults.elements.point.backgroundColor = "white";
Chart.defaults.elements.point.borderColor = "white";
Chart.defaults.font.size = 15;
$(document).ready(function () {
  var data = $("#totalByDay").data("plot");
  var dates = data.date;
  var views = data.views;
  var videos_data = [];
  var videos_labels = [];
  for (var i = 0; i < dates.length; i++) {
    var index = data.videos.date.indexOf(dates[i]);
    if (index !== -1) {
      videos_data.push(data.videos.views[index]);
      videos_labels.push(data.videos.name[index]);
    } else {
      videos_data.push(null);
      videos_labels.push(null);
    }
  }

  var ctx = $("#totalByDay").get(0).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: "Views",
          data: views,
          fill: false,
          tension: 0.3,
        },
        {
          label: "Videos",
          data: videos_data,
          fill: false,
          tension: 0.3,
          type: "bar", // Set the type of the chart to 'bar'
        },
      ],
    },
    options: {
      plugins: {
        tooltip: {
          callbacks: {
            title: function (context) {
              var index = context[0].dataIndex;
              return videos_labels[index] || "";
            },
          },
        },
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: "Total Views by Day",
          font: {
            size: 25,
          },
        },
      },
      maintainAspectRatio: false,
      aspectRatio: 0.7,
      responsive: true,
    },
  });
});
