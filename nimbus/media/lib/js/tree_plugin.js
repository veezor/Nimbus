function mount_tree(data, root_path, get_tree_path) {
    root = $("*[path="+root_path+"]");
    root.addClass('directory_open');
    var ul = $("<ul>").addClass("open").hide();
    ul.insertAfter($("*[path="+root_path+"]"));
    for (var item in data) {
        path = data[item];
        root_path_re = new RegExp("^" + root_path, "g");
        path_name = path.replace(root_path_re, '');

        var input = $("<input>").attr("type", "checkbox").attr("name", "path").val(path);
        
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

        input.change(function(){
            checked = $(this).attr("checked") && "checked" || "";
            $(this).parent().find('input').attr("checked", checked);
        });
        input.prependTo(file);

        var li = $("<li>").addClass(attr_class).addClass(mime_class);
        file.appendTo(li);
        li.appendTo(ul);
    }
    ul.slideDown();
    $(".tree a").unbind("click").click(function()
    {
        update_tree($(this).attr("path"), get_tree_path);
        return false;
    });
    
    link.find(".wait").remove();
}

function update_tree(root_path, get_tree_path) {
    attributes = {path: root_path};
    
    job_id = $('#jobs_list').val();
    if (job_id) {
        attributes['job_id'] = job_id;
    }
    
    computer_id = $('#computer_id').val();
    if (computer_id) {
        attributes['computer_id'] = computer_id;
    }
    
    link = $("*[path="+root_path+"]");
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
               mount_tree(data, root_path, get_tree_path);
           },
           "json");
}