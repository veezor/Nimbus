$(document).ready(function(){
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
    // colorbox scripts
    $(".schedule").colorbox({
        href: "/backup/schedules/add",
        scrolling:false
    });
    $(".fileset").click(function(){
        //$.colorbox.close();
        if ($("#id_procedure-computer").val())
        {
            $.colorbox({
                href: "/backup/filesets/add/"+$("#id_procedure-computer").val()
            });
        }
        else
        {
            $.colorbox({html:"<h2>Atenção!</h2><h3>Você precisa escolher um computador</h3>"});
        }
        return false;
    });
});