$(function() {
	$( ".checkboxes" ).buttonset();
});

WEEK = {0: 'Domingo',
		1: 'Segunda-feira',
		2: 'Terça-feira',
		3: 'Quarta-feira',
		4: 'Quinta-feira',
		5: 'Sexta-feira',
		6: 'Sabado'};

$(document).ready(function(){
	// Inicio do adicionar mensal
	$('#month_button').click(function(){
		var month_days = $('.month');
		var month_array = new Array();
		for (var i = 0; i < 31; i++) {
	        if (month_days[i].checked == true) {
                month_array.push(i+1);
            }
        }
		var hours_array = get_hours()
		var minutes_array = get_minutes();
		if (month_array.length == 0) {
			alert("Você deve escolher ao menos um dia do mês para executar o backup");
		} else if ($('#id_month-level').val() == 'None'){
			alert("Escolha o tipo de backup que deseja realizar");
		} else {
			var level_id = $('#id_month-level')[0].value
			var level = $('#id_month-level')[0].options[level_id].text;
			for (var day = 0; day < month_array.length; day++) {
				for (var hour = 0; hour < hours_array.length; hour++) {
					for (var minute = 0; minute < minutes_array.length; minute++) {
						SCHEDULES.push({'kind_id': 1, 'status': 'new', 'kind': 'Mensal', 'level_id': level_id, 'level': level, 'day_num': month_array[day], 'day': month_array[day], 'hour': pad(hours_array[hour], 2), 'minute': pad(minutes_array[minute],2)});
					}
				}
			}
			update_inventory();
		}
    });
	// fim do adicionar mensal

	// inicio do adicionar semanal
	$('#week_button').click(function(){
		var week_days = $('.week');
		var week_array = new Array();
		for (var i = 0; i < 7; i++) {
	        if (week_days[i].checked == true) {
                week_array.push(i);
            }
        }
		var hours_array = get_hours()
		var minutes_array = get_minutes();
		if (week_array.length == 0) {
			alert("Você deve escolher ao menos um dia da semana para executar o backup");
		} else if ($('#id_week-level').val() == 'None'){
			alert("Escolha o tipo de backup que deseja realizar");
		} else {
			var level_id = $('#id_week-level')[0].value
			var level = $('#id_week-level')[0].options[level_id].text;
			for (var day = 0; day < week_array.length; day++) {
				for (var hour = 0; hour < hours_array.length; hour++) {
					for (var minute = 0; minute < minutes_array.length; minute++) {
						SCHEDULES.push({'kind_id': 2, 'status': 'new', 'kind': 'Semanal', 'level_id': level_id, 'level': level, 'day_num': week_array[day], 'day': WEEK[week_array[day]], 'hour': pad(hours_array[hour], 2), 'minute': pad(minutes_array[minute],2)});
					}
				}
			}
			update_inventory();
		}
    });
	// fim do adicionar semanal
	
	// inicio do adicionar diário
	$('#day_button').click(function(){
		var hours_array = get_hours()
		var minutes_array = get_minutes();
		if ($('#id_day-level').val() == 'None'){
			alert("Escolha o tipo de backup que deseja realizar")
		} else {
			var level_id = $('#id_day-level')[0].value
			var level = $('#id_day-level')[0].options[level_id].text;
			for (var hour = 0; hour < hours_array.length; hour++) {
				for (var minute = 0; minute < minutes_array.length; minute++) {
					SCHEDULES.push({'kind_id': 3, 'status': 'new', 'kind': 'Diário', 'level_id': level_id, 'level': level, 'day_num': 0, 'day': 'Todos', 'hour': pad(hours_array[hour], 2), 'minute': pad(minutes_array[minute],2)});
				}
			}
			update_inventory();
		}
    });
	// fim do adicionar diário
	
	// inicio do adicionar de hora em hora
	$('#hour_button').click(function(){
		var minutes_array = get_minutes();
		if ($('#id_hour-level').val() == 'None'){
			alert("Escolha o tipo de backup que deseja realizar")
		} else {
			var level_id = $('#id_hour-level')[0].value
			var level = $('#id_hour-level')[0].options[level_id].text;
			for (var minute = 0; minute < minutes_array.length; minute++) {
				SCHEDULES.push({'kind_id': 4, 'status': 'new', 'kind': 'Hora em hora', 'level_id': level_id, 'level': level, 'day_num': 0, 'day': 'Todos', 'hour': '##', 'minute': pad(minutes_array[minute],2)});
			}
			update_inventory();
		}
    });
	// fim do adicionar de hora em hora
});
function update_inventory() {
	$("#inventory")[0].innerHTML = "<thead><tr><th>Remover</th><th>Tipo</th><th>Frequência</th><th>Dia</th><th>Hora</th></tr></thead>";
	for (var index in SCHEDULES) {
		var ob = SCHEDULES[index];
        // if (ob['status'] != 'deleted') {
		    var line = '<tr class="' + ob['status'] + '_run"><td><span onclick="remove_schedule(' + index + ')" class="remove_schedule" >Icone</span></td><td>' + ob['level'] + '</td><td>' + ob['kind'] + '</td><td>' + ob['day'] + '</td><td>' + ob['hour'] + ':' + ob['minute'] + '</td></tr>';
		    $("#inventory").append(line);
        // };
	};
	uncheck_all();
};
function remove_schedule(id) {
    if (SCHEDULES[id]['status'] == 'new') {
        SCHEDULES.splice(id, 1);        
    } else if (SCHEDULES[id]['status'] == 'deleted') {
        SCHEDULES[id]['status'] = 'old';
    } else {
        SCHEDULES[id]['status'] = 'deleted';
    }
	update_inventory()
};
function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}
function get_hours() {
	var hours = $('.hours');
	var hours_array = new Array();
	for (var i = 0; i < 24; i++) {
        if (hours[i].checked == true) {
            hours_array.push(i)
        }
    };
	if (hours_array.length == 0) {
		hours_array = [0];
	}
	return hours_array;
}
function get_minutes() {
	var minutes = $('.minutes');
	var minutes_array = new Array();
	for (var i = 0; i < 60; i++) {
        if (minutes[i].checked == true) {
            minutes_array.push(i)
        }
    };
	if (minutes_array.length == 0) {
		minutes_array = [0];
	}
	return minutes_array;
}
function uncheck_all() {
	$('.month').attr('checked', false).button('refresh');
	$('.week').attr('checked', false).button('refresh');
	$('.hours').attr('checked', false).button('refresh');
	$('.minutes').attr('checked', false).button('refresh');			
}
function submit_all() {
	if (SCHEDULES.length == 0) {
		alert("Você deve definir ao menos um agendamento");
		return false;
	}
	var schedule_name = $("#schedule_name").val();
	if (EDITING == true) {
	    var post_url = '/schedules/do_edit/';
	    var post_data =  {'main': 'edit', 'name': schedule_name, 'id': EDITED_SCHEDULE_ID};
	} else {
	    var post_url = '/schedules/do_add/';
	    var post_data =  {'main': 'new', 'name': schedule_name, 'is_model': IS_MODEL};
	}
	var status = new Array();
	$.ajax({
        type: "POST",
		async: false,
        url: post_url,
        data: post_data,
        success: function(j) {
            var schedule_response = jQuery.parseJSON(j);
            console.log(schedule_response);
			if (schedule_response['status'] == 'ok') {
				TMP_SCHEDULE_ID = schedule_response['new_id'];
				for (var index in SCHEDULES) {
					console.log(SCHEDULES[index]);
					if (SCHEDULES[index]['status'] != 'old') {
    					SCHEDULES[index]['schedule_id'] = TMP_SCHEDULE_ID; 
    					$.ajax({
    			            type: "POST",
    						async: false,
    			            url: post_url,
    			            data: SCHEDULES[index],
    			            success: function(j) {
    			                var run_response = jQuery.parseJSON(j);
    							if (run_response['status'] == 'ok') {
    								status.push(true);
    							}
    			            }
    			        });
                    } else {
                        status.push(true);
                    }
				}						
			}
        }
    });
	if (status.length == SCHEDULES.length) {
		alert('Agendamento criado com sucesso');
		SCHEDULE_ID = TMP_SCHEDULE_ID;
		return true;				
	} else {
		alert('Ocorreu um erro na criação do agendamento');
		return false;
	}
}
function create_schedule() {
	var status = submit_all();
	if (status == true) {
		$.facebox.close();
		set_schedule();
	}
}