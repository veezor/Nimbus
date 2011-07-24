$(document).ready(function(){

    function create_chart(obj_id, data, ticks, chart_type, labels) {
        var fill = false;
        var render = $.jqplot.PieRenderer;
        var highlighter_show = true;
        var cursor_show = true;
        var pointLabels_show = false;

        if (chart_type == 'bar') {
            var render = $.jqplot.BarRenderer;
            highlighter_show = false;
            cursor_show = false;
            pointLabels_show = true;
        } else if (chart_type == 'area') {
            var render = $.jqplot.LineRenderer;
            var fill = true;
        }

        $.jqplot(obj_id, [data], {
            seriesDefaults: {
                renderer: render,
                pointLabels: {
                    location:'s',
                    show: pointLabels_show,
                    labels: labels
                },
                fill: true,
                /* color: '#95BACB', */
                color: '#67c7a1',
                markerOptions: {
                    show: true,
                    lineWidth: 5,
                    size: 5,
                    color: 'red'
                }
            },
            axes: {
                xaxis: {
                    renderer: $.jqplot.CategoryAxisRenderer,
                    ticks: ticks,
                    min: 0
                },
                yaxis: {
                    tickOptions:{ 
                        mark: 'outside',    // Where to put the tick mark on the axis
                                    // 'outside', 'inside' or 'cross',
                        showMark: true,
                        showGridline: true, // wether to draw a gridline (across the whole grid) at this tick,
                        markSize: 4,        // length the tick will extend beyond the grid in pixels.  For
                                            // 'cross', length will be added above and below the grid boundary,
                        show: true,         // wether to show the tick (mark and label),
                        showLabel: true,    // wether to show the text label at the tick,
                        formatString: '%.2f',
                    },
                    min: 0,
                    //max: 2000
                     
                }
            },
            highlighter: { show:highlighter_show },
            cursor: { show: cursor_show },
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
