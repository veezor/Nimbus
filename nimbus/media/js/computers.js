$(document).ready(function(){
    // mostra detalhes do fileset
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
        return false;
    });
    function update_groups() {
        groups = $('#id_groups');
 a       groups.empty();
        
        $.post('/computers/group/list/', {'ajax': true}, function(data){
            for (group in data) {
                group = data[group];
                $('<option>').attr('value', group['pk']).text(group['fields']['name']).appendTo(groups);
            }
        }, "json");
    }
    
    $('#add_group').click(function(){
        $('.add_group').slideToggle();
        return false;
    });
    $('#add_group_submit').click(function(){
        group_name = $('#add_group_name').val();
        $.post('/computers/group/add/', {'name': group_name}, function(data){
            if (data.message == 'success') {
                $('.add_group').slideUp();
                update_groups();
                alert(gettext("Group") + group_name + gettext("added."));
            } else {
                alert(gettext('It was not possible to insert the group. A group with the same name already exists.'));
            }
        }, "json");
        return false;
    });
    $('#add_group_cancel').click(function(){
        $('.add_group').slideUp();
        return false;
    });
});
