$(document).ready(function(){
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
                    // alert(response.message);
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
            submit_filter();
            if (typeof NOT_ASYNC != "undefined") {
                $('#main_form').submit()
            } else {
                async_submit();
            }
        }
	});
});

function discard_unused_fileset(fileset_id) {
    $.ajax({
        type: "POST",
        url: "/filesets/reckless_discard/",
        data: {"fileset_id": fileset_id},
        success: function(j) {
            console.log(j);
		}
    });
}

// CODIGO REFERENTE AOS FILTROS
$(document).ready(function(){
    filter_extentions = {
        "audio": ["*.mp3", "*.wav", "*.ogg"],
        "video": ["*.avi", "*.mpg", "*.mp4"],
        "documentos": ["*.doc", "*.docx", "*.pdf"],
        "imagens": ["*.jpg", "*.bmp", "*.png"]
    };
    for (var kind in filter_extentions) {
        $("#filter_table").append('<tr><td class="include_button ' + kind + '"><img src="/media/icons/seta_esquerda.png"></td><td><span title="'+ kind.charAt(0).toUpperCase() + kind.slice(1) +': '+ filter_extentions[kind] +'" class="with_tooltip">'+ kind.charAt(0).toUpperCase() + kind.slice(1) +'</span></td><td class="exclude_button '+ kind +'"><img src="/media/icons/seta_direita.png"></td></tr>'); 
    };
    $("#filter_table").append(''+
    '<tr id="custom_filter_tr"><td class="include_button custom"><img src="/media/icons/seta_esquerda.png"></td><td><input type="text" id="custom_filter"></input></td><td class="exclude_button custom"><img src="/media/icons/seta_direita.png"></td></tr>' + 
	'<tr><td></td><td><button class="css3button negative" id="adv_filter_button">Filtro avançado</button></td><td></td></tr>');
    $(".with_tooltip").tooltip();

});

function submit_filter() {
    if (($(".included").length + $(".excluded").length) >= 1) {
        console.log("bateu");
        var n = 0;
        for (var i = 0; i < $(".included").length; i++) {
            // $('#main_form').append('<input name="include_form" type="hidden" value="'+$(".included")[i].textContent+'">');
            var new_filter = '\n' + 
                '<input type="hidden" name="wildcards-'+ n +'-expression" value="' + $(".included")[i].textContent + '">\n' +
                '<input type="hidden" name="wildcards-' + n + '-fileset">\n' +
                '<input type="hidden" name="wildcards-' + n + '-kind" value="I">\n' +
                '<input type="hidden" name="wildcards-' + n + '-id">\n';
            $('#main_form').append(new_filter);
            n++;
        }
        for (var i = 0; i < $(".excluded").length; i++) {
            // $('#main_form').append('<input name="exclude_form" type="hidden" value="'+$(".included")[i].textContent+'">');
            var new_filter = '\n' + 
                '<input type="hidden" name="wildcards-'+ n +'-expression" value="' + $(".excluded")[i].textContent + '">\n' +
                '<input type="hidden" name="wildcards-' + n + '-fileset">\n' +
                '<input type="hidden" name="wildcards-' + n + '-kind" value="E">\n' +
                '<input type="hidden" name="wildcards-' + n + '-id">\n';
            $('#main_form').append(new_filter);
            n++;
        };
		$('#id_wildcards-TOTAL_FORMS').val(n);
    }
};
function custom_filter() {
    return [$("#custom_filter").val()];
}
function exist_in(item, list) {
    for (var i = 0; i < list.length; i++) {
        if (list[i] == item) {
            return true;
        }
    }
    return false;
}
function includeList() {
    var list = new Array();
    for (var i = 0; i < $(".included").length; i++) {
        list.push($(".included")[i].textContent);
    }
    return list
}
function excludeList() {
    var list = new Array();
    for (var i = 0; i < $(".excluded").length; i++) {
        list.push($(".excluded")[i].textContent);
    }
    return list
}


$(".include_button").click(function(){
    var filter = $(this)[0].className.replace("include_button ","");
    if (filter=="custom") {
        var filterlist = custom_filter();
    } else {
        var filterlist = filter_extentions[filter];
    }
    var current_excludes = excludeList();
    var current_includes = includeList();
    var dont_put = new Array();
    var do_put = new Array();
    for (var i = 0; i < filterlist.length; i++) {
        if (exist_in(filterlist[i], current_excludes) == true) {
            dont_put.push(filterlist[i]);
        } else {
            do_put.push(filterlist[i]);
        }
    };
    if (dont_put.length >= 1) {
        alert("Um ou mais filtros não serão adicionados pois já se encontram na lista de 'Ignorar estes arquivos'.\n Os filtro abaixo não serão adicionados\n"+dont_put)
    }
    for (var i = 0; i < do_put.length; i++) {
        if (exist_in(do_put[i], current_includes) == false) {
            $("#include_list").append("<li onclick='$(this).remove();'><span  class='added_filter included'>"+do_put[i]+"</span></li>");		
        }
	};
});

$(".exclude_button").click(function(){
    var filter = $(this)[0].className.replace("exclude_button ","");
    if (filter=="custom") {
        var filterlist = custom_filter();
    } else {
        var filterlist = filter_extentions[filter];
    }
    var current_excludes = excludeList();
    var current_includes = includeList();
    var dont_put = new Array();
    var do_put = new Array();
    for (var i = 0; i < filterlist.length; i++) {
        if (exist_in(filterlist[i], current_includes) == true) {
            dont_put.push(filterlist[i]);
        } else {
            do_put.push(filterlist[i]);
        }
    };
    if (dont_put.length >= 1) {
        alert("Um ou mais filtros não serão adicionados pois já se encontram na lista de 'Apenas estes arquivos'.\n Os filtro abaixo não serão adicionados\n"+dont_put)
    }
    for (var i = 0; i < do_put.length; i++) {
        if (exist_in(do_put[i], current_excludes) == false) {
            $("#exclude_list").append("<li onclick='$(this).remove();'><span  class='added_filter excluded'>"+do_put[i]+"</span></li>");		
        }
	};
});
$("#adv_filter_button").click(function(){
    $("#custom_filter_tr").show();
    $("#adv_filter_button").hide();
    return false;
});
$("#show_filters_button").click(function(){
    $("#filter_hidden_block").show();
    $("#show_filters_button").hide();
    return false;
});
