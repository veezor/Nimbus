$(document).ready(function(){
    var profile = $('<div class="clear">').html('<a href="'+ $("#profile").val() +'">Adicionar novo perfil</a>');
    $('#id_profile').parents().filter('p').append(profile);
    
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
        return false;
    });
    
    get_tree_path = "/backup/get_tree/";
    
    $('#update_tree').click(function()
    {
        update_tree('/', get_tree_path, undefined, undefined, undefined, '#computer_id');
        return false;
    });

    $(".tree a").click(function()
    {
        update_tree($(this).attr("path"), get_tree_path, undefined, undefined, undefined, '#computer_id');
        return false;
    });
    
    $('#schedule_id').change(function(){
        if ($('#schedule_id :selected').attr('id') == 'new_schedule') {
            $('#schedule').slideDown();
        } else {
            $('#schedule').slideUp();
        }
    });
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
    
});