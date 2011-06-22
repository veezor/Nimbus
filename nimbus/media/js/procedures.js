// JavaScript para mostrar os status dos jobs nos hist—rico
$(document).ready(function(){
    $('.job_line').click(function(){
        var job_id = $(this)[0].id;
        var job_details = $('#' + job_id + '_details')[0];
        $('#status_box')[0].innerHTML = job_details.innerHTML;
    });
});

$(document).ready(function(){
    $('.edit-fileset').click(function(){
        var fileset_id = $(this)[0].id;
        selected_val = $('#select_' + fileset_id)[0].value;
        console.log(selected_val);
        if (selected_val == "") {
            alert("Escolha um computador para usar como base de arquivos");
            return false;
        }
        locattion = $(this)[0].href;
        $(this)[0].href = locattion + selected_val;
    });
});

$(document).ready(function(){
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
});

function set_fileset() {
    if (typeof FILESET_ID != "undefined") {
        $("#id_procedure-fileset").append("<option value="+FILESET_ID+">"+FILESET_NAME+"</option>");
        $("#id_procedure-fileset").val(FILESET_ID);
        $("#uniform-id_procedure-fileset").hide();
        $("#fileset_button").html("<span>Modificar [" + FILESET_NAME + "]</span>");
        $("#fileset_button").attr('href', "/filesets/" + FILESET_ID + "/edit/");            
    }
};

$(document).ready(function(){
    $('#schedule_button').click(function() {
        var computer_id = $('#id_procedure-computer').val();
        var fileset_id = $('#id_procedure-fileset').val();
        var storage_id = $('#id_procedure-storage').val();
        var retention_time = $('#id_procedure-pool_retention_time').val()
        var name = $('#id_procedure-name').val();
        var form = $('#to_schedule_form');
        form.append('<input type="hidden" name="computer_id" value="' + computer_id + '"/>');
        form.append('<input type="hidden" name="fileset_id" value="' + fileset_id + '"/>');
        form.append('<input type="hidden" name="storage_id" value="' + storage_id + '"/>');
        form.append('<input type="hidden" name="retention_time" value="' + retention_time + '"/>');
        form.append('<input type="hidden" name="procedure_name" value="' + name + '"/>');
        form.append('<input type="hidden" name="first_step" value="true"/>');
        form.submit();
        return false;
    });
    set_fileset();
    $('#toggle_fileset_choice').click(function() {
        $("#uniform-id_procedure-fileset").toggle('slow');
        $('#toggle_fileset_choice').html("<span>N‹o usar modelo</span>");
        $("#fileset_button").toggle('slow')
        console.log('teste')
    });
});
// open async windows
$(document).ready(function(){
    $('#fileset_button').click(function(){
        if ($('#id_procedure-computer').val())
        {
            jQuery.facebox({ ajax: $('#fileset_button')[0].href+$('#id_procedure-computer').val() });
        }
        else
        {
            jQuery.facebox('Voc precisa esolher um computador');
        }
        return false;
    });
});
// new document.ready to organize
$(document).ready(function(){
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

});
/* Slider */
$(document).ready(function(){
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
	});
	
	$("#pool_retention_alt").keyup(function(){
		var value = this.value;
		//alert(value);
		$("#id_procedure-pool_retention_time").val(value);
	});
});























