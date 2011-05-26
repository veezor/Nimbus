// open async windows
$(document).ready(function(){
    $('.schedules').click(function(){
        jQuery.facebox({ ajax: '/schedules/add' });
        return false;
    });
    $('.filesets').click(function(){
        if ($('#id_procedure-computer').val())
        {
            jQuery.facebox({ ajax: '/filesets/add/'+$('#id_procedure-computer').val() });
        }
        else
        {
            jQuery.facebox('Você precisa esolher um computador');
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
        if (_checked) {
            $('.' + _class).addClass('active');
        } else {
            $('.' + _class).removeClass('active');
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