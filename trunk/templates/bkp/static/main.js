function set_backup_type() {
    $('form select[name=type]').change(
        function() {
            backup_type = $(this).children().filter(':selected').val();
            change_backup_type(backup_type);
        }
    );
    $('form select[name=type]').change();
}

function change_backup_type(backup_type) {
    $('#id_schedule_type').val(backup_type);
    switch (backup_type.toLowerCase()) {
        case 'weekly':
            // Do something...
            //console.log('weekly');
            $('.mtriggform').hide('fast');
            $('.wtriggform').show('fast');
            $('.triggform_message').hide('fast');
            break;
        case 'monthly':
            // Do something more...
            //console.log('monthly');
            $('.mtriggform').show('fast');
            $('.wtriggform').hide('fast');
            $('.triggform_message').hide('fast');
            break;
        default:
            // Go away.
            //console.log('default');
            $('.mtriggform').hide('fast');
            $('.wtriggform').hide('fast');
            $('.triggform_message').show('fast');
    }
}

$(document).ready(function() {
    // Execute function to start the application.
    set_backup_type();
});
