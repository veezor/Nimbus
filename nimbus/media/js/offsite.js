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

    $("#id_rate_limit").hide();
    $("#offsite_form #id_active_upload_rate").change(function(){
        var ps = $("#id_rate_limit");
        if( $("#id_active_upload_rate").attr('checked')){
            ps.slideDown("fast");
        } else {
            ps.slideUp("fast");
            ps.val(-1);
        }
    });

    var initial_upload = $("#id_rate_limit").val();
    if(initial_upload == -1) {
        $("#id_rate_limit").hide();
        $("label[for=id_rate_limit]").hide();
        $("#id_active_upload_rate").attr('checked', false).change();
    } else {
        $("#id_active_upload_rate").attr('checked', true).change();
    }

    $("#id_active_upload_rate").change(function(){
        if ($("#id_active_upload_rate").is(':checked')){
            $("#id_rate_limit").show();
            $("label[for=id_rate_limit]").show();
            if (initial_upload == -1)
                initial_upload = 200;
            $("#id_rate_limit").val(initial_upload);
        } else {
            $("#id_rate_limit").hide();
            $("label[for=id_rate_limit]").hide();
            $("#id_rate_limit").val("-1");
        }
    });

    function update_table() {
        var table = $('.request_list');
        var url = $('.atualizar_agora').attr("rel");
        if($('.atualizar_agora').length){
            $.post(url, {ajax: 1}, function(data)
            {
                table.find('tbody tr').remove();
                for (var item in data) {
                    down = data[item];
                    tr = $('<tr>');
                    caminho_arquivo = $('<td>').text(down.fields.filename);
                    criado_em = $('<td>').text(down.fields.created_at);
                    tentativas = $('<td>').html(down.fields.attempts + " <small>(" +gettext("Last: ") + down.fields.last_attempt + ")</small>");
                    transferencia = $('<td>').html(down.fields.friendly_rate + " <small>( "+gettext("remain:") + down.fields.estimated_transfer_time + ")</small>");
                    wrapper = $('<div>').addClass("concluido_wrapper").attr({"title": down.fields.finished_percent + "%"+ gettext("done.")});
                    percent = $('<div>').addClass("concluido_percent").css("width", down.fields.finished_percent + "%").html("&nbsp;");
                    concluido = $('<td>').append(wrapper.append(percent));

                    tr.append(caminho_arquivo).append(criado_em).append(tentativas).append(transferencia).append(concluido);
                    tr.appendTo(table.find('tbody'));
                }
            },
            "json");
        }
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
