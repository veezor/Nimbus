GLOBAL_COUNTER = 0;
function mount_tree(data, root_path, get_tree_path, tree_class, input_type, input_name, depends) {


    if (data.type = 'error' && data.message) {
        $('#mensagem_erro_fileset').html(data.message).show();
        $(".wait").remove();
        return false;
    } else {
        $('#mensagem_erro_fileset').html('').hide();
    }

    if (!tree_class) {
        tree_class = '.tree';
    }
    if (!input_type) {
        input_type = 'checkbox';
    }
    if (!input_name) {
        input_name = 'path';
    }
    
    root = $(tree_class + " *[path="+root_path+"]");
    root.addClass('directory_open');
    var ul = $("<ul>").addClass("open").hide();
    ul.insertAfter($(tree_class + " *[path="+root_path+"]"));

    $(tree_class + " *[path="+root_path+"]").click(function(){
        alert("bla");
    });
    link = $(tree_class + " *[path="+root_path+"]");
    link.append($("<div class='wait'></div>"));
    
    total = data.length;
    contador = 0;
    for (var item in data) {
        contador = contador + 1;
        if (contador > total) {
            break;
        }
        
        path = data[item];
        if (!path) {
            continue;
        }

        path = new String(path);
        root_path_re = new RegExp("^" + root_path, "g");
        path_name = path.replace(root_path_re, '');

        var input = $("<input>").attr("type", input_type).attr("name", input_name+GLOBAL_COUNTER).val(path);
        GLOBAL_COUNTER = GLOBAL_COUNTER + 1;
        
        // If is a directory.
        if (path.match("/$") == "/" || path.match("\\$") == "\\") {
            attr_class = "directory";
            mime_class = "folder";
            var inner = $("<a>").attr("href", "#").attr("path", path).text(path_name);
        } else {
            attr_class = "file";
            if (path_name.split('.').length > 1) {
                mime_class = "ext_" + $(path_name.split('.')).eq(-1)[0].toLowerCase();
            } else {
                mime_class = "";
            }
            
            var inner = $("<span>").html(path_name);
        }

        var file = $("<span>").html(inner);
        var counter = 0;
        if (input_type != "radio") {
            input.change(function(){
                checked = $(this).attr("checked") && "checked" || "";
                $(this).parent().find('input').attr("checked", checked);
                
                if (!checked) {
                    atual = $(this).parent().parent().parent().parent();
                    for (var i = 0; i < $(this).val().split('/').length - 2; i++) {
                        atual.find('input').eq(0).attr('checked', '');
                        atual = atual.parent().parent().parent().parent();
                    }

                    $.each($(':input').serializeArray(), function(i, field) {
                        if (field.value == path)
                        {
                            $("#id_filepath_set-TOTAL_FORMS").val(counter-1);
                            $("#id_filepath_set-INITIAL_FORMS").val(counter-1);
                            $("#id_filepath_set-MAX_NUM_FORMS").val(counter-1);
                            $("[name="+field.name+"]").remove();
                        }
                    });
                }
                else
                {
                    // creates input hidden for validation
                    var input_path = "<input type='text' value='"+path+"' class='hdn' id='id_filepath_set-"+counter+"-path' name='filepath_set-"+counter+"-path' />";
                    var input_fileset = "<input type='text'  value='"+path+"' class='hdn' id='id_filepath_set-"+counter+"-fileset' name='filepath_set-"+counter+"-fileset' />";
                    var input_id = "<input type='text'  value='"+path+"' class='hdn' id='id_filepath_set-"+counter+"-id' name='filepath_set-"+counter+"-id' />";
                    counter++;
                    $('#submit_fileset').after(input_path);

                    $("#id_filepath_set-TOTAL_FORMS").val(counter);
                    $("#id_filepath_set-INITIAL_FORMS").val(counter);
                    $("#id_filepath_set-MAX_NUM_FORMS").val(counter);
                }
            });
        }
        input.prependTo(file);

        var li = $("<li>").addClass(attr_class).addClass(mime_class);
        file.appendTo(li);
        li.appendTo(ul);
    }
    ul.slideDown();
    $(tree_class + " a").unbind("click").click(function()
    {
        update_tree($(this).attr("path"), get_tree_path, tree_class, input_type, input_name, depends);
        return false;
    });
    
    link.find(".wait").remove();
}

function update_tree(root_path, get_tree_path, tree_class, input_type, input_name, depends) {
    if (!tree_class) {
        tree_class = '.tree';
    }
    if (!input_type) {
        input_type = 'checkbox';
    }
    if (!input_name) {
        input_name = 'path[]';
    }
    attributes = {path: root_path};
    
    job_id = $('#jobs_list').val();
    if (job_id) {
        attributes['job_id'] = job_id;
    }
    
    computer_id = $('#computer_id').val();
    if (computer_id) {
        attributes['computer_id'] = computer_id;
    }
    else {
        $('#mensagem_erro_fileset').html('Um computador deve ser selecionado antes.').show();
        return false;
    }
    
    if (depends == '#computer_id' && !computer_id) {
        $('#mensagem_erro_fileset').html('Um computador deve ser selecionado antes.').show();
        return false;
    } else if (depends == '#job_id' && !job_id) {
        $('#mensagem_erro_fileset').html('Um job deve ser selecionado antes.').show();
        return false;
    } else {
        $('#mensagem_erro_fileset').html('').hide();
    }
    
    link = $(tree_class + " *[path="+root_path+"]");
    link.find(".wait").remove();
    link.append($("<div class='wait'></div>"));

    wrapper = link.parent();

    if (wrapper.find('ul').length) {
        var ul = wrapper.find('>ul');
        if (ul.hasClass('open')) {
            ul.removeClass('open').addClass('closed');
            link.removeClass('directory_open').addClass('directory_closed');
            wrapper.find('ul').slideUp();
        } else if (ul.hasClass('closed')) {
            ul.removeClass('closed').addClass('open');
            link.removeClass('directory_closed').addClass('directory_open');
            wrapper.find('ul').slideDown();
            wrapper.find('>ul').slideDown();
        }
        link.find(".wait").remove();
        return false;
    }
    
    $.post(get_tree_path,
           attributes,
           function(data) {
               mount_tree(data, root_path, get_tree_path, tree_class, input_type, input_name, depends);
           },
           "json");

}