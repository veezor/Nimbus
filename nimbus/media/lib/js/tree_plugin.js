function mount_tree(data, root_path, get_tree_path, tree_class, input_type, input_name, depends) {
    if (data.type = 'error' && data.message) {
        $('#mensagem_erro_fileset').html(data.message).show();
        return false;
    } else {
        $('#mensagem_erro_fileset').html('').hide();
    }
    
    root = $(tree_class + " *[path="+root_path+"]");
    root.addClass('directory_open');
    var ul = $("<ul>").addClass("open").hide();
    ul.insertAfter($(tree_class + " *[path="+root_path+"]"));
    for (var item in data) {
        path = data[item];
        if (!path) {
            continue;
        }
        root_path_re = new RegExp("^" + root_path, "g");
        path_name = path.replace(root_path_re, '');

        var input = $("<input>").attr("type", input_type).attr("name", input_name).val(path);
        
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
    // console.log(input_type);
    if (!input_type) {
        input_type = 'checkbox';
    }
    if (!input_name) {
        input_name = 'path';
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
    link.append($("<div class='wait'>"));
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