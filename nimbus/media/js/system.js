$(document).ready(function(){
    $('.toggle').click(function(){
        var target = $(this).attr('ref');
        $(this).parent().parent().find('.' + target).slideToggle();
        return false;
    });
    
    $('#form_ping').submit(function(){
        $('#mensagem').slideUp().empty();
        $('#mensagem').html('<img src="/media/icons/loading_bar.gif" />'+gettext("Wait..."));
        $('#mensagem').slideDown();
        
        var type = $('#type').val();
        $.post("/system/create_or_view_network_tool/", {ip: $('#ip').val(), type: type},
            function(data){
                $('#mensagem').empty();
                if (!data) {
                    $('#mensagem').html(gettext("Error running ping");
                    return false;
                }
                
                $('#mensagem').html(data.msg.replace(/\n/g, "<br/>"));
            },
            "json");
        return false;
    });
    
    function update_table(table) {
        table = $('.request_list');
        $.post($(".atualizar_agora").attr("rel"), {ajax: 1}, function(data)
        {
            table.find('tbody tr').remove();
            for (var item in data) {
                down = data[item];
                tr = $('<tr>');
                pid = $('<td>').text(down.fields.pid);
                name = $('<td>').text(down.fields.name);
                criado_em = $('<td>').text(down.fields.created_at);
                estado = $('<td>').text(down.fields.status);
                
                tr.append(pid).append(name).append(criado_em).append(estado);
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
        $('.tempo_restante').text(countDownTime);
    }

    function startit(){
        $('.tempo_restante').text(countDownTime);
        countDown();
        counter=setInterval(countDown, 1000);
    }

    startit();
    $('.atualizar_agora').click(function(){
        update_table();
        countDownTime = countDownInterval;
        clearInterval(counter);
        startit();
    });
});
