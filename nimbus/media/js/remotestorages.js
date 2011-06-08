$(document).ready(function(){
    var data = [
        ['Ocupado', 80],['Livre', 20]
    ];
    var plot1 = jQuery.jqplot ('chart1', [data], 
    { 
        title: "Espa&ccedil;o em Disco",
        seriesColors: [ "#EAA228", "#579575"],
        seriesDefaults: {
            // Make this a pie chart.
            renderer: jQuery.jqplot.PieRenderer, 
            rendererOptions: {
                // Put data labels on the pie slices.
                // By default, labels show the percentage of the slice.
                showDataLabels: true
            }
        }, 
        legend: { show:true, location: 'e' }
    });
});