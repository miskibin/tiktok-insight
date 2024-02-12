$(document).ready(function () {
  var data = $("#followers").data("plot");
  var dates = data.date;
  var followers = data.followers;
  var difference = data.difference;

  var ctx = $("#followers").get(0).getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [
        {
          label: "Followers",
          data: followers,
          fill: false,
          tension: 0.3,
        },
        {
          type: "bar",
          label: "Difference",
          data: difference,
          fill: false,
        },
      ],
    },
    options: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: "Followers",
        font: {
          size: 25,
        },
      },
      maintainAspectRatio: false,
      aspectRatio: 0.7,
      responsive: true,
    },
  });
});
