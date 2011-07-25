$(document).ready(function(){
    // Accordeon for procedure history
    $(".hide").slideUp();
    $('.job_line').click(function(){
        $(".hide").slideUp();
        var next = $(this).next();
        if (next.css('display') == 'none')
            next.slideDown();
        else
            next.slideUp();
    });
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
        console.log(selected_val);
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
    $(".red").click(function(){
        if (!confirm("Tem certeza?"))
            return false;
    });
    // facebox stuff
    //$.facebox.settings.opacity = 0.3;
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

    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
    });

    get_tree_path = "/filesets/get_tree/";

    $('#update_tree').click(function()
    {
        update_tree('/', get_tree_path, undefined, undefined, undefined, '#computer_id');
        return false;
    });

    $('#schedule_id').change(function(){
        if ($('#schedule_id :selected').attr('id') == 'new_schedule') {
            $('#schedule').slideDown();
        } else {
            $('#schedule').slideUp();
        }
    });

    $(".tree a").click(function()
    {
        update_tree($(this).attr("path"), get_tree_path, undefined, undefined, undefined, '#computer_id');
        return false;
    });

    $('.profile').change(function(){
        if ($('.profile:checked').attr('id') == 'profile_0') {
            $('.novo_perfil').slideDown();
        } else {
            $('.novo_perfil').slideUp();
        }
    });
    $('.profile').change();


    $('#schedule_id').change();

    $('.schedule_activate').change(function(){
        _checked = $(this).attr('checked');
        _class = $(this).attr('id');
        console.log(_class)
        if (_checked) {
            $('.' + _class).addClass('active');
            $('.' + _class + '_error').show();
        } else {
            $('.' + _class).removeClass('active');
            $('.' + _class + '_error').hide();
        }
    });
    $('.schedule_activate').change();

    $('#fileset_id').change(function(){
        if ($('#fileset_id :selected').attr('id') == 'new_fileset') {
            $('#fileset').slideDown();
        } else {
            $('#fileset').slideUp();
        }
    });
    $('#fileset_id').change();
    $('#filepath_template').clone().appendTo('.filepaths').show();

    function remover_path(obj) {
        $(obj).parent().remove();
        if ($('#filepath_template').parent().children().length == 1) {
            adicionar_path();
        }
    }

    function adicionar_path(obj) {
        if (obj) {
            $('#filepath_template').clone().insertAfter($(obj).parent()).show();
        } else {
            $('#filepath_template').clone().appendTo('.filepaths').show();
        }
        $('.filepaths .add').unbind('click').click(function(){
            adicionar_path(this);
        });
        $('.filepaths .del').unbind('click').click(function(){
            remover_path(this);
        });
    }

    $('.filepaths .add').click(function(){
        adicionar_path(this);
    });

    $('.filepaths .del').click(function(){
        remover_path(this);
    });
    // register new computer
    $("#computer_id").change(function(){
        var vlw = $(this).val();
        if (vlw == 'add'){
            window.location = '/computers/add/';
        }
    });

    $('.schedule_activate').change(function(){
        _checked = $(this).attr('checked');
        _class = $(this).attr('id');
        if (_checked) {
            $('.' + _class).addClass('active');
        } else {
            $('.' + _class).removeClass('active');
        }
    });
    $('.schedule_activate').change();
    // suggests the name
    var last_computer;
    var last_schedule;
    var last_storage;
    $("#id_procedure-computer").change(function(){
        var proc_name = $("#id_procedure-name").val();
        var add_name = $("#id_procedure-computer :selected").text();
        if (proc_name.indexOf(add_name) == -1)
        {
            if (add_name == '---------'){add_name = "";}
            proc_name += add_name + " ";
            $("#id_procedure-name").val(proc_name);
            $("#id_procedure-name").val(proc_name.replace(last_computer, ""));
            last_computer = add_name + " ";
        }
        else
        {
            $("#id_procedure-name").val(proc_name.replace(last_computer, ""));
            $("#id_procedure-name").val(proc_name.replace(add_name + " ", ""));
            last_computer = add_name + " ";
        }
        return false;
    });
    $("#id_procedure-schedule").change(function(){
        var schedule_name = $("#id_procedure-name").val();
        var add_name = $("#id_procedure-schedule :selected").text();
        if (schedule_name.indexOf(add_name) == -1)
        {
            if (add_name == '---------'){add_name = "";}
            schedule_name += add_name + " ";
            $("#id_procedure-name").val(schedule_name);
            $("#id_procedure-name").val(schedule_name.replace(last_schedule, ""));
            last_schedule = add_name + " ";
        }
        else
        {
            $("#id_procedure-name").val(schedule_name.replace(last_schedule, ""));
            $("#id_procedure-name").val(schedule_name.replace(add_name + " ", ""));
            last_schedule = add_name + " ";
        }
        return false;
    });
    $("#id_procedure-schedule").change(function(){
        var schedule_name = $("#id_procedure-name").val();
        var add_name = $("#id_procedure-storage :selected").text();
        if (schedule_name.indexOf(add_name) == -1)
        {
            if (add_name == '---------'){add_name = "";}
            schedule_name += add_name + " ";
            $("#id_procedure-name").val(schedule_name);
            $("#id_procedure-name").val(schedule_name.replace(last_storage, ""));
            last_storage = add_name + " ";
        }
        else
        {
            $("#id_procedure-name").val(schedule_name.replace(last_storage, ""));
            $("#id_procedure-name").val(schedule_name.replace(add_name + " ", ""));
            last_storage = add_name + " ";
        }
        return false;
    });
    $("#id_procedure-storage").change(function(){
        var storage_name = $("#id_procedure-name").val();
        var add_name = $("#id_procedure-storage :selected").text();
        if (storage_name.indexOf(add_name) == -1)
        {
            if (add_name == '---------'){add_name = "";}
            storage_name += add_name + " ";
            $("#id_procedure-name").val(storage_name);
            $("#id_procedure-name").val(storage_name.replace(last_storage, ""));
            last_storage = add_name + " ";
        }
        else
        {
            $("#id_procedure-name").val(storage_name.replace(last_storage, ""));
            $("#id_procedure-name").val(storage_name.replace(add_name + " ", ""));
            last_storage = add_name + " ";
        }
        return false;
    });
    /* Slider */
	var maximun = 121;
	$(".pool_new_value").hide();
	$(".add_new_pool").hide();
	$("#slider_value").html("10");
	$("#slider").slider({ 
		animate: true, step: 1, max: maximun, min: 0, value: 10
	});
	$("#slider").bind("slide slidechange", function(){
		var value = $("#slider").slider("option", "value");
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
		$(".pool_value").hide();
		$(".pool_new_value").show();
		$("#pool_retention_alt").focus();
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
    FILESET_ID = $(".fileset_return").val();
    if (typeof FILESET_ID != "undefined") {
        $("#id_procedure-fileset").append("<option value="+FILESET_ID+">Usar o fileset criado</option>");
        $("#id_procedure-fileset").val(FILESET_ID);
        $("#uniform-id_procedure-fileset").hide('slow');
        $("#discard_fileset").show('slow')
        $("#fileset_button").html("<span>Modificar</span>");
        $("#fileset_button").attr('href', "/filesets/" + FILESET_ID + "/edit/");   
        $(".fileset_return").val(FILESET_ID);         
    }
};
function set_schedule() {
    SCHEDULE_ID = $(".schedule_return").val();
    if (typeof SCHEDULE_ID != "undefined") {
        $("#id_procedure-schedule").append("<option value="+SCHEDULE_ID+">Usar o agendamento criado</option>");
        $("#id_procedure-schedule").val(SCHEDULE_ID);
        $("#uniform-id_procedure-schedule").hide('slow');
        $("#discard_schedule").show('slow')
        $("#schedule_button").html("Modificar");
        $("#schedule_button").attr('href', "/schedules/" + SCHEDULE_ID + "/edit/"); 
        $(".schedule_return").val(SCHEDULE_ID);
    }
};
function unset_schedule() {
    $("#uniform-id_procedure-schedule").show('slow');
    $("#discard_schedule").hide('slow')
    $("#schedule_button").html("<span>Criar outro agendamento</span>");
    $("#schedule_button").attr('href', "/schedules/add/");   
    $(".schedule_return").val("");         
};
function unset_fileset() {
    $("#uniform-id_procedure-fileset").show('slow');
    $("#discard_fileset").hide('slow')
    $("#fileset_button").html("<span>Criar outro fileset</span>");
    $("#fileset_button").attr('href', "/filesets/add/");            
};