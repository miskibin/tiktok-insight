Chart.defaults.color = "white";
Chart.defaults.elements.point.backgroundColor = "white";
Chart.defaults.elements.point.borderColor = "white";
Chart.defaults.font.size = 15;
$(document).ready(function () {
  var data = $("#gendersDistribution").data("plot");
  var genders = data.genders;
  var distribution = data.distributions.map(function (x) {
    return x * 100;
  });

  var ctx = $("#gendersDistribution").get(0).getContext("2d");
  new Chart(ctx, {
    type: "pie",
    data: {
      labels: genders,
      datasets: [
        {
          data: distribution,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        title: {
          display: true,
          text: "Gender Distribution",
        },
      },
      maintainAspectRatio: false,
      aspectRatio: 0.7,
      responsive: true,
    },
  });
});
