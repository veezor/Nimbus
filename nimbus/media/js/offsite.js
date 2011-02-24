$(document).ready(function(){
    $('#offsite_form #id_active').change(function(){
        input_active = $('#offsite_form #id_active');
        ps = input_active.parents().filter('p').siblings().filter(':not(p:last)');
        if (input_active.attr('checked')) {
            ps.slideDown();
        } else {
            ps.slideUp();
        }
    }).change();

    $("#id_upload_rate").hide();
    $("#offsite_form #id_active_upload_rate").change(function(){
        var ps = $("#id_upload_rate");
        if( $("#id_active_upload_rate").attr('checked')){
            ps.slideDown("fast");
            ps.val(200);
        } else {
            ps.slideUp("fast");
            ps.val(-1);
        }
    });

    var initial_upload = $("#id_upload_rate").val();
    if(initial_upload == -1) {
        $("#id_upload_rate").hide();
        $("label[for=id_upload_rate]").hide();
        $("#id_active_upload_rate").attr('checked', false).change();
    } else {
        $("#id_active_upload_rate").attr('checked', true).change();
    }

    $("#id_active_upload_rate").change(function(){
        if ($("#id_active_upload_rate").is(':checked')){
            $("#id_upload_rate").show();
            $("label[for=id_upload_rate]").show();
            if (initial_upload == -1)
                initial_upload = 200;
            $("#id_upload_rate").val(initial_upload);
        } else {
            $("#id_upload_rate").hide();
            $("label[for=id_upload_rate]").hide();
            $("#id_upload_rate").val("-1");
        }
    });

    function update_table() {
        var table = $('.request_list');
        var url = $('.atualizar_agora').attr("rel");
        $.post(url, {ajax: 1}, function(data)
        {
            table.find('tbody tr').remove();
            for (var item in data) {
                down = data[item];
                tr = $('<tr>');
                caminho_arquivo = $('<td>').text(down.fields.filename);
                criado_em = $('<td>').text(down.fields.created_at);
                tentativas = $('<td>').html(down.fields.attempts + " <small>(última: " + down.fields.last_attempt + ")</small>");
                transferencia = $('<td>').html(down.fields.friendly_rate + " <small>(restante: " + down.fields.estimated_transfer_time + ")</small>");

                wrapper = $('<div>').addClass("concluido_wrapper").attr({"title": down.fields.finished_percent + "% concluído."});
                percent = $('<div>').addClass("concluido_percent").css("width", down.fields.finished_percent + "%").html("&nbsp;");
                concluido = $('<td>').append(wrapper.append(percent));

                tr.append(caminho_arquivo).append(criado_em).append(tentativas).append(transferencia).append(concluido);
                tr.appendTo(table.find('tbody'));
            }
        },
        "json");
    }

    var countDownInterval = 20;
    var countDownTime = countDownInterval + 1;
    var counter = undefined;

    function countDown(){
        countDownTime--;
        if (countDownTime <= 0){
            $('.tempo_restante').text(countDownTime);
            countDownTime = countDownInterval;
            clearInterval(counter);
            update_table();
            return startit();
        }
        $('.tempo_restante').html(countDownTime);
    }

    function startit(){
        $('.tempo_restante').html(countDownTime);
        countDown();
        counter = setInterval(countDown, 1000);
    }

    $('.atualizar_agora').click(function(){
        update_table();
        countDownTime = countDownInterval;
        clearInterval(counter);
        startit();
    });

    startit();
});
