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
                week_array.push(i+1)
            }
            $("#id_week-days").val(week_array);
        }
	});
});
