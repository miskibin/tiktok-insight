Chart.defaults.color = "white";
Chart.defaults.elements.point.backgroundColor = "white";
Chart.defaults.elements.point.borderColor = "white";
Chart.defaults.font.size = 15;
$(document).ready(function () {
  var data = $("#activity").data("plot");
  var hours = data.hours;
  var avg_followers = data.avg_followers;
  var ctx = $("#activity").get(0).getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: hours,
      datasets: [
        {
          data: avg_followers,
          borderWidth: 1,
        },
        {
          type: "line",
          data: avg_followers,
          tension: 0.5,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: true,
          text: "Followers activity by hour",
        },
      },
      maintainAspectRatio: false,
      aspectRatio: 0.7,
      responsive: true,
    },
  });
});
