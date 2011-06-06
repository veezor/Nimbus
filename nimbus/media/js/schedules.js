$(document).ready(function(){
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
            }
            else if (field.name == 'schedule.weekly.day')
            {
                week_days += field.value+",";
            }
            else
            {
                dataString += field.name+"="+field.value+"&";
            }
        });
        dataString += "schedule.monthly.day="+month_days+"&schedule.weekly.day="+week_days+"&schedule-is_model="+is_model;
        $.ajax({
            type: "POST",
            url: "/schedules/add/",
            data: dataString,
            success: function() {
                alert("Cadastro efetuado com MUITO MUITO sucesso!");
                //$(document).trigger('close.facebox');
            },
            error: function(){
                alert('Houve um problema com a requisição');
                //$(document).trigger('close.facebox');
            }
        });
    };
    $(".use_it").click(function(){
        commit_settings(0);
    });
    $(".use_and_save_it").click(function(){
        commit_settings(1);
    });
});
