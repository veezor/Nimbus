// Todo o código abaixo e referente apenas ao STEP 4
$(document).ready(function(){
    $('#buscar_arquivos').click(function(){
        do_search();
    });
    $('#add_checked').click(function(){
        for (var f = 0; f < $(".full_path").length; f++) {
            if ($(".full_path")[f].checked == true) {
                append_file_to_restore($(".full_path")[f].value)
            }
        }
        return false;
    });
    $("#submit_files").click(function() {
        if ($(".added_file").length == 0) {
            alert(gettext("No file selected for restore.");
            return false;
        } else {
            for (var f = 0; f < $(".added_file").length; f++) {
                console.log($(".added_file")[f].textContent);
                $("#step4_form").append("<input type='hidden' name='paths' value='"+ $(".added_file")[f].textContent +"'></input>");
            }
            $("#step4_form").submit();
        }
    });
    // Trata se alguem apertar ENTER no campo de busca de arquivos
    $("#pattern").keypress(function(e) {
        code= (e.keyCode ? e.keyCode : e.which);
        if (code == 13) {
            do_search();
            e.preventDefault();
        }
    });
});
    function do_search() {
        get_tree_path = "/restore/get_tree/";
        $(".search_result").remove();
		$("#search_result_list").append("<li class='search_result'>"+gettext("Searching files")+"<img src='/media/icons/loading_bar.gif'/></li>");    
        // jobid = job_id.value
        pattern = $('#pattern').val();
        root_path = '/';
    
        $.post("/restore/get_tree_search_file/",
               {job_id: job_id.value, pattern: pattern},
               function(data) {
                   $(".search_result").remove();
                   if (data.length == 0) {
                       $("#search_result_list").append("<li class='search_result'>"+gettext("No file found")+"</li>");
                   } else {
                       for (var f = 0; f < data.length; f++) {
                           append_file_to_search(data[f]);
                       }
                   }
               },
               "json");
        return false;
    }
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
// Fim do código do STEP 4