$(document).ready(function(){
    
    function update_groups() {
        groups = $('#id_groups');
        groups.empty();
        
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
                alert('Grupo "' + group_name + '" adicionado.');
            } else {
                alert('Não foi possível inserir o grupo. Um grupo com o mesmo nome já existe.');
            }
        }, "json");
        return false;
    });
    $('#add_group_cancel').click(function(){
        $('.add_group').slideUp();
        return false;
    });
    
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
        return false;
    });
});