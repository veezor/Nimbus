$(document).ready(function(){
    // Accordeon for procedure history
	$("#accordion").accordion({ collapsible: true, active: false });
    $('.job_line').mouseover(function(){
        $(this).addClass('over');
    });
    $('.job_line').mouseout(function(){
        $(this).removeClass('over');
    });
    
    // JavaScript para mostrar os status dos jobs nos histórico
    $('.edit-fileset').click(function(){
        var fileset_id = $(this)[0].id;
        selected_val = $('#select_' + fileset_id)[0].value;
        if (selected_val == "") {
            alert("Escolha um computador para usar como base de arquivos");
            return false;
        }
        locattion = $(this)[0].href;
        jQuery.facebox({ ajax: locattion + selected_val });
        return false;
    });
    $('.edit-schedule').click(function(){
        locattion = $(this)[0].href;
        jQuery.facebox({ ajax: locattion });
        return false;
    });
    // table styles
    $("tbody tr").mouseover(function(){
        $(this).addClass("hvr");
        $(this).removeClass("nrl");
    });
    $("tbody tr").mouseout(function(){
        $(this).addClass("nrl");
        $(this).removeClass("hvr");
    });
    /* Asks 'are you sure?' on delete action */
    // Não importa se voce clica em 'ok' ou 'cancel', a acao eh executada assim mesmo
    // $(".red").click(function(){
    //     if (!confirm("Tem certeza?"))
    //         return false;
    // });

    // facebox stuff
    $.facebox.settings.opacity = 0.7;
    $('#fileset_button').click(function(){
        if ($('#id_procedure-computer').val())
        {
            //jQuery.facebox('Você precisa escolher um computador');
            jQuery.facebox({ ajax: $('#fileset_button')[0].href+$('#id_procedure-computer').val() });
        }
        else
        {
            jQuery.facebox('Você precisa escolher um computador');
        }
        return false;
    });
    $('#schedule_button').click(function(){
        $.facebox(function(){
            $.facebox({ ajax: $('#schedule_button')[0].href});
        });
        return false;
    });
    /* Slider */
	var maximun = 121;
    // $(".pool_new_value").hide();
	$("#id_procedure-pool_retention_time").hide();
	$(".add_new_pool").hide();
	$("#slider_value").html("10");
    var slider = $("#slider")
	$("#slider").slider({ 
		animate: true, step: 1, max: maximun, min: 1, value: 10
	});
	$("#slider").bind("slide", function(){
		var value = slider.slider("option", "value");
		$("#slider_value").html(value);
		$("#id_procedure-pool_retention_time").val(value);
		if (value > (maximun-20))
		{
			$(".add_new_pool").show();
		}
		else if (value <= (maximun-20))
		{
			$(".add_new_pool").hide();
		}
	});
	
	$(".add_new_pool").click(function(){
		$("#slider").hide();
		$("#slider_value").html("Em");
		$("#id_procedure-pool_retention_time").show();
		$("#id_procedure-pool_retention_time").focus();
		$(".add_new_pool").hide();
		return false;
	});
	
	$("#pool_retention_alt").keyup(function(){
		var value = this.value;
		//alert(value);
		$("#id_procedure-pool_retention_time").val(value);
	});
});

// default functions
function set_fileset() {
    // FILESET_ID = $(".fileset_return").val();
    if (typeof FILESET_ID != "undefined") {
        $("#id_procedure-fileset").append("<option value="+FILESET_ID+">Usar o fileset criado</option>");
        $("#id_procedure-fileset").val(FILESET_ID);
        $("#id_procedure-fileset").hide("slow");
        $("#uniform-id_procedure-fileset").hide('slow');
        $("#discard_fileset").show('slow');
        $("#fileset_button").html("<span>Modificar</span>");
        $("#fileset_button").attr('href', "/filesets/" + FILESET_ID + "/edit/");   
        $(".fileset_return").val(FILESET_ID);         
    }
};
function set_schedule() {
    // SCHEDULE_ID = $(".schedule_return").val();
    if (typeof SCHEDULE_ID != "undefined") {
        $("#id_procedure-schedule").append("<option value="+SCHEDULE_ID+">Usar o agendamento criado</option>");
        $("#id_procedure-schedule").val(SCHEDULE_ID);
        $("#id_procedure-schedule").hide('slow');
        $("#uniform-id_procedure-schedule").hide('slow');
        $("#discard_schedule").show('slow');
        $("#schedule_button").html("Modificar");
        $("#schedule_button").attr('href', "/schedules/" + SCHEDULE_ID + "/edit/"); 
        $(".schedule_return").val(SCHEDULE_ID);
    }
};
function unset_schedule() {
    $("#uniform-id_procedure-schedule").show('slow');
    $("#discard_schedule").hide('slow');
    $("#schedule_button").html("<span>Criar outro agendamento</span>");
    $("#schedule_button").attr('href', "/schedules/add/");   
    $(".schedule_return").val("");
    $("#id_procedure-schedule").val('');
    for (var i = 0; i <= $("#id_procedure-schedule")[0].length; i++){
        if ($("#id_procedure-schedule")[0][i].value == SCHEDULE_ID) {
            $("#id_procedure-schedule")[0].remove(i);
        }
    }
    $("#id_procedure-schedule").show('slow');
    discard_unused_schedule(SCHEDULE_ID);
};
function unset_fileset() {
    $("#uniform-id_procedure-fileset").show('slow');
    $("#discard_fileset").hide('slow');
    $("#fileset_button").html("<span>Criar outro fileset</span>");
    $("#fileset_button").attr('href', "/filesets/add/");
    $("#id_procedure-fileset").val('');
    for (var i = 0; i <= $("#id_procedure-fileset")[0].length; i++){
        if ($("#id_procedure-fileset")[0][i].value == FILESET_ID) {
            $("#id_procedure-fileset")[0].remove(i);
        }
    }
    $("#id_procedure-fileset").show("slow");
    discard_unused_fileset(FILESET_ID);
};
