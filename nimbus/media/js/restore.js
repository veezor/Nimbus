$(document).ready(function(){
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
        return false;
    });

    $(".tree a").click(function()
    {
        get_tree_path = "/restore/get_tree/";
        update_tree($(this).attr("path"), get_tree_path, '.tree');
        return false;
    });

    $(".tree_computer a").click(function()
    {
        get_tree_path = "/restore/get_client_tree/";
        update_tree($(this).attr("path"), get_tree_path, ".tree_computer", "radio", "path_restore");
        return false;
    });

    $('#buscar_arquivos').click(function(){
        get_tree_path = "/restore/get_tree/";
        
        job_id = $('#jobs_list').val();
        pattern = $('#pattern').val();
        root_path = '/';
        $('.tree .directory.first ul').remove().removeClass("open");
        
        $.post($("#url_tree").val(),
               {job_id: job_id, pattern: pattern},
               function(data) {
                   mount_tree(data, root_path, get_tree_path)
               },
               "json");
        return false;
    });
    
    $('#procedure_id').change(function()
    {
        if ($(this).val()) {
            $('.restore_step_1').slideDown();
        } else {
            $('.restore_step_1').slideUp();
        }
    });
    $('#procedure_id').change();
    
    $('#computer_id').change(function()
    {
        var computer_id = $(this).val();
        $.getJSON('/restore/get_procedures/' + computer_id + '/', {}, function(data)
        {
            if (data['error']) {
                $('.computer_error').html($('<p>').text(data['error'])).addClass("message error").show('slow');
            }
        
            $('#procedure_id').empty();
            $('<option>').attr('value', '').text(' - Selecione - ').appendTo('#procedure_id');
            for (proc in data) {
                proc = data[proc];
                if (proc['fields'] && proc['fields']['name']) {
                    $('<option>').attr('value', proc['pk']).text(proc['fields']['name']).appendTo("#procedure_id");
                }
            }
            $('.procedure_select').slideDown();
        });
    });
    $('#computer_id').change();

    $('#procedure_id').change(function()
    {
        if ($(this).val()) {
            $('.restore_step_1').slideDown();
        } else {
            $('.restore_step_1').slideUp();
        }
    });
    $('#procedure_id').change();
    
    $('.submit_step_1').click(function(){
        data_inicio = $('#data_inicio').val();
        data_inicio = data_inicio.replace(/\//gi,"-");
        data_fim = $('#data_fim').val();
        data_fim = data_fim.replace(/\//gi,"-");
        computer_id = $('#computer_id').val();
        procedure_id = $('#procedure_id').val();
    
        $('.restore_step_2').slideUp();
        $('.restore_step_3').slideUp();
        $('.restore_step_4').slideUp();
        $('.restore_step_5').slideUp();
        
        if (data_inicio && data_fim) {
            //alert('/restore/get_jobs/' + procedure_id + '/' + data_inicio + '/' + data_fim + '/');
            $.getJSON(
                '/restore/get_jobs/' + procedure_id + '/' + data_inicio + '/' + data_fim + '/',
                function(data)
                {
                    $("#jobs_list").empty();
                    if (data) {
                        // TODO: Populate the jobs list.
                        $("<option>").val("").text(" - " + data.length + " jobs, selecione um  - ").attr("selected", "selected").appendTo("#jobs_list");
                        // exemplo
                        //$("<option>").val("2").text(" Job de exemplo, selecione este ").attr("selected", "selected").appendTo("#jobs_list");
                        for (var i in data) {
                            job = data[i];
                            if (job.fields && job.fields.realendtime) {
                                $("<option>").val(job.pk).text(job.fields.realendtime + ' - ' + job.fields.jobfiles + ' arquivos').appendTo("#jobs_list");
                            }
                        }
                        $("#jobs_list").change();
                        $('.restore_step_2').slideDown();
                    }
                }
            );
        }
    
        return false;
    });
    
    $('.submit_step_1').click();
    
    
    $('#jobs_list').change(
        function(){
            $('.restore_step_3').slideUp();
            
            $('.tree .directory.first ul').remove().removeClass("open");
            
            if ($(this).val()) {
                $('.restore_step_3').slideDown();
            } else {
                $('.restore_step_3').slideUp();
            }
        }
    ).click();
    
    $(".open_step_4").click(function(){
        $(".restore_step_4").slideDown();
        return false;
    });
    
    
    $('#pattern').keydown(
        function(e){
            if (e.keyCode == 13) {
                $('#buscar_arquivos').click();
                return false;
            }
        }
    )
});