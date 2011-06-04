$(document).ready(function(){
	$(".month_checkbox").click(function(){
    	var month_array = new Array();
	    var month_days = $(".month_checkbox");
	    for (var i = 0; i < 31; i++) {
	        if (month_days[i].checked == true) {
                month_array.push(i+1)
            }
            $("#id_month-days").val(month_array);
        }
	});
	$(".week_checkbox").click(function(){
    	var week_array = new Array();
	    var week_days = $(".week_checkbox");
	    for (var i = 0; i < 7; i++) {
	        if (week_days[i].checked == true) {
                week_array.push(i)
            }
            $("#id_week-days").val(week_array);
        }
	});
    var selected_month_days = $("#id_month-days").val().split(",");
    for (month_day in selected_month_days) {
        month_day_id = "#month_day_" + selected_month_days[month_day];
        $(month_day_id).attr('checked', true);
    };
    var selected_week_days = $("#id_week-days").val().split(",");
    for (week_day in selected_week_days) {
        week_day_id = "#week_day_" + selected_week_days[week_day];
        $(week_day_id).attr('checked', true);
    } 
});
