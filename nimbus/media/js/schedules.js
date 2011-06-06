$(document).ready(function(){
<<<<<<< HEAD
	var append = "";
	$(".schedule_checkbox").click(function(){
		if (this.checked == true)
		{
			var value = this.value;
			if ($("#id_month-days").val() == "")
			{
				append = value;
			}
			else
			{
				append = $("#id_month-days").val() + "," + value;
			}
			$("#id_month-days").val(append);
		}
		else
		{
			var value = this.value;
			var month_value = $("#id_month-days").val();
			var remove = month_value.replace(value+",", "");
			$("#id_month-days").val(remove);
		}
	});
    function commit_settings(is_model){
    	console.log(is_model);
        var dataString = "";
        var month_days = "";
        var week_days = "";
        $.each($('#schedule_new').serializeArray(), function(i, field) {
            if (field.name == 'schedule.monthly.day')
            {
                month_days += field.value+",";
=======
	$(".month_checkbox").click(function(){
    	var month_array = new Array();
	    var month_days = $(".month_checkbox");
	    for (var i = 0; i < 31; i++) {
	        if (month_days[i].checked == true) {
                month_array.push(i+1)
>>>>>>> 20564a8f0783193bf00e6d2e73541b40f718f947
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
