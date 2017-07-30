/**
 * Retrieves chart data with jquery for chart
 */

$(document).ready(function() {
    var chart = document.getElementById('chart').getContext('2d');
    var options = {responsive: false, legend: {display: false}, tooltips: {mode: 'index', intersect: false, titleFontSize: 15, bodyFontSize: 15}, scales: {yAxes: [{ticks: {beginAtZero: true}}]}};

    $.ajax({
        url: "/api/get/chart-data/7"
    }).then(function(data) {
        myChart = new Chart(chart, {type: 'line', data: data, options: options});
    });
    $("#7").addClass("selected");

    getChartData= function(days) {
        var daysID = "#" + days
        $(".days").removeClass("selected");
        $(daysID).addClass("selected");

        $.ajax({
            url: "/api/get/chart-data/" + days
        }).then(function(data) {
            myChart.destroy();
            myChart = new Chart(chart, {type: 'line', data: data, options: options});
        });
    };
});
