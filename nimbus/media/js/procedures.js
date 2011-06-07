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
        form.submit()
    });
});
