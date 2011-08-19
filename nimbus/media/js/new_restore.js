$(document).ready(function(){
    $('#buscar_arquivos').click(function(){
        get_tree_path = "/restore/get_tree/";
        $(".search_result").remove();
    
        job_id = "745"
        pattern = $('#pattern').val();
        root_path = '/';
    
        $.post("/restore/get_tree_search_file/",
               {job_id: job_id, pattern: pattern},
               function(data) {
                   if (data.length == 0) {
                       $("#search_result_list").append("<li class='search_result'>Nenhum arquivo encontrado</li>");
                   } else {
                       for (var f = 0; f < data.length; f++) {
                           append_file_to_search(data[f]);
                       }
                   }
               },
               "json");
        return false;
    });
    $('#add_checked').click(function(){
        for (var f = 0; f < $(".full_path").length; f++) {
            if ($(".full_path")[f].checked == true) {
                append_file_to_restore($(".full_path")[f].value)
            }
        }
        return false;
    });
});
    function path_kind(path) {
        if (path[path.length -1] == "/") {
            var kind = "directory";
        } else {
            var kind = "file";
        };
        return kind
    };
    function append_file_to_search(file) {
        var kind = path_kind(file);
        $("#search_result_list").append('<li class="'+kind+' search_result" onClick="append_file_to_restore($(this)[0].textContent);"><span class="listed_file">' + file + '</span></li>')
    };
    function append_file_to_restore(file) {
        var kind = path_kind(file);
        $("#restore_file_list").append('<li class="'+kind+' selected_file" onClick="$(this).remove();"><span class="added_file">' + file + '</span></li>')
    }
