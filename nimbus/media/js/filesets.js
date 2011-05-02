$(document).ready(function(){
    $('#filepath_template').clone().appendTo('.filepaths').show();
    
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
    });
    
    get_tree_path = "/backup/get_tree/";
    
    $('#update_tree').click(function()
    {
        update_tree('/', get_tree_path);
        return false;
    });

    $(".tree a").click(function() {
        if (!document.getElementsByClassName('wait')[0]) {
            update_tree($(this).attr("path"), get_tree_path);
        } else {
            $('.wait').remove();
        }
        return false;
    });
    
    function adicionar_path(obj) {
        if (obj) {
            $('#filepath_template').clone().insertAfter($(obj).parent()).show();
        } else {
            $('#filepath_template').clone().appendTo('.filepaths').show();
        }
        
        $('.filepaths .add').click(function(){
            adicionar_path(this);
        });
        
        $('.filepaths .del').unbind('click').click(function(){
            remover_path(this);
        });
    }
    
    function remover_path(obj) {
        $(obj).parent().remove();
        if ($('#filepath_template').parent().children().length == 1) {
            adicionar_path();
        }
    }

    $('.filepaths .add').click(function(){
        adicionar_path(this);
    });

    $('.filepaths .del').click(function(){
        remover_path(this);
    });

    $('#computer_id').change(function(){
        $('.tree > li ul').first().remove();
    });
    
    
});