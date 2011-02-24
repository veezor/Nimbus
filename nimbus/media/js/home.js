$(document).ready(function(){

    function create_chart(obj_id, data, ticks, chart_type, labels) {
        var fill = false;
        var render = $.jqplot.PieRenderer;

        if (chart_type == 'bar') {
            var render = $.jqplot.BarRenderer;
        } else if (chart_type == 'area') {
            var render = $.jqplot.LineRenderer;
            var fill = true;
        }

        $.jqplot(obj_id, [data], {
            seriesDefaults: {
                renderer: render,
                pointLabels: { location:'s', show: true, labels: labels },
                fill: true,
                color: '#95BACB'
            },
            axesDefaults: {
                tickOptions: {
                    //formatString: "%.2f"
                }
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: ticks,
                    min: 0
                },
                yaxis: {
                    min: 0
                }
            },
            highlighter: { show: false }
        });
    };


    $('.jqplotchart').each(function(){
        var chart_id = $(this).attr('id');
        var data = $(this).children().filter('chartdata').text().split(',');
        data = $.map(data, function(e){
            return parseFloat(e);
        });
        var labels = $(this).children().filter('chartlabels').text().split(',');
        var header = $(this).children().filter('chartheader').text().split(',');
        var chart_type = $(this).attr('charttype');
        $(this).text('');

        create_chart(chart_id, data, header, chart_type, labels);
    });
});
