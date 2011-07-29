$(document).ready(function(){
    $("input:checkbox").addClass("no-style");
    $('#filepath_template').clone().appendTo('.filepaths').show();
    
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
    });
    
    get_tree_path = "/filesets/get_tree/";
    
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
$(document).ready(function(){
    function async_submit() {
        $(".field_error").hide();
        $.ajax({
            type: "POST",
            url: $('#main_form')[0].action,
            data: $('#main_form').serialize(),
            success: function(j) {
                var response = jQuery.parseJSON(j);
                if (response.status == true) {
                    FILESET_ID = response.fileset_id;
                    $(".fileset_return").val(FILESET_ID);
                    FILESET_NAME = response.fileset_name;
                    alert(response.message);
                    $.facebox.close();
                    set_fileset();
                    //location.reload();
                    href = window.location.href;
                    if (href.search("/procedures/profile/list/") > 0){
                        window.location = "/procedures/profile/list/#fileset_"+response.fileset_id;
                        location.reload();
                    }
                } else {
                    $("#field_error_" + response.error).show();
                    alert(response.message);
                }
            }
        });  
    };
    $('#submit_button').click(function(){
		var all_paths = $('.full_path');
		var checked_paths = new Array()
		for (var i = 0; i < all_paths.length; i++) {
			if (all_paths[i].checked == true) {
				checked_paths.push(all_paths[i].value);
			};
		};
		var inicial = parseInt($('#id_files-INITIAL_FORMS')[0].value)
		var total = inicial + checked_paths.length
		$('#id_files-TOTAL_FORMS').val(total);
		for (var i = 0; i < checked_paths.length; i++) {
		    var n = i + inicial;
			var new_path_field = '\n' + 
			'<input id="id_files-'+ n + '-path" type="hidden" name="files-'+ n +'-path" maxlength="2048" class="text" value="' + checked_paths[i] + '">\n' +
			'<input type="hidden" name="files-' + n + '-fileset" id="id_files-' + n + '-fileset">\n' +
			'<input type="hidden" name="files-' + n + '-id" id="id_files-' + n + '-id">\n';
			$('#main_form').append(new_path_field);
		};
        // $('#main_form').submit();
        if (total == 0) {
            alert("Nenhum arquivo foi selecionado")
        } else {
            if (typeof NOT_ASYNC != "undefined") {
                $('#main_form').submit()
            } else {
                async_submit();
            }
        }
	});
});
