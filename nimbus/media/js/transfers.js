
function set_part_focus(who) {
    $(".part").removeClass("selected")
    var queue_id = who[0]
    var arrow_position = queue_id.offsetLeft + (queue_id.offsetWidth / 2) - 6;
    $("#marker").animate({"left": arrow_position+"px"}, "slow", function(){
        $(".upload_info").hide();
        $("#info_" + queue_id.id).show();
        $("#" + queue_id.id).addClass("selected")
    });    
}
function get_data() {
    $.ajax({
        type: "POST",
        url: "/offsite/upload_queue_data/",
        data: "Nada",
        // async: false,
        dataType: "json",
        success: function(j) {
            $("#upload_done").text(j['upload_done']);
            $("#upload_total").text(j['upload_total']);
            var percent_done = (100 * j['upload_done'] / j['upload_total'])
            $("#percent_done").text(percent_done.toFixed(1));
            $("#current_speed").text(j['current_speed']);
            $("#eta_str").text(j['eta_str']);
            $("#end_time_str").text(j['end_time_str']);
            // VERIFICA SE UM BLOCO NAO EXISTE MAIS E O APAGA SE NESCESSÁRIO
            var blocks_list = new Array()
            for (var item = 0; item < $(".part").length; item++) {
                blocks_list.push($(".part")[item].id);
            }
            for (var item = 0; item < blocks_list.length; item++) {
                var item_exists = false;
                for (var i = 0; i < j['uploads'].length; i++) {
                    if (blocks_list[item] == "queue_item_" + j['uploads'][i]['id']) {
                        item_exists = true;
                    }
                }
                if (item_exists == false) {
                    if ($("#" + blocks_list[item]).hasClass("selected") == true) {
                        $("#" + blocks_list[item]).remove();
                        $("#" + $(".part")[0].id).addClass("selected");
                        $("#info_" + $(".selected")[0].id).show();
                    } else {
                        $("#" + blocks_list[item]).remove()   ;                     
                    }
                    $("#info_" + blocks_list[item]).remove();
                }
            }
            // FIM DE VERIFICA SE UM BLOCO NAO EXISTE MAIS E O APAGA SE NESCESSÁRIO
            // VERIFICA SE EXISTE UM NOVO BLOCO E O CRIA
            var blocks_list = new Array()
            for (var item = 0; item < $(".part").length; item++) {
                blocks_list.push($(".part")[item].id);
            }
            for (var i = 0; i < j['uploads'].length; i++) {
                u = j['uploads'][i];
                var item_exists = false;
                for (var item = 0; item < blocks_list.length; item++) {
                    // console.log(" b " + blocks_list[item]);
                    if ("queue_item_" + u['id'] == blocks_list[item]) {
                        item_exists = true;
                    }
                }
                if (item_exists == false) {
                    console.log("queue_item_" + u['id']);
                    var new_block = '<div id="queue_item_'+u['id']+'" class="part"></div>';
                    if (i == 0) {
                        $(new_block).insertBefore("#" + $(".part")[0].id)
                    } else {
                        $(new_block).insertAfter("#queue_item_" + j['uploads'][i-1]['id']);                        
                    }
                }
            }
            // FIM DE VERIFICA SE EXISTE UM NOVO BLOCO E O CRIA
            for (var i = 0; i < j['uploads'].length; i++) {
                u = j['uploads'][i];
                if ($("#queue_item_" + u['id']) == []) {
                    console.log("Adicione o item")
                } else {
                    // REDIMENSIONA OS BLOCOS E MOVE A SETA
                    $("#queue_item_" + u['id']).animate({"width": u['portion'] + "%"}, "slow", function(){
                        if ($(this).hasClass("selected") == true) {
                            var new_arrow_position = $(this)[0].offsetLeft + ($(this)[0].offsetWidth / 2) - 6;
                            $("#marker").animate({"left": new_arrow_position+"px"}, "slow")
                        }
                    })
                    // FIM DE REDIMENSIONA OS BLOCOS E MOVE A SETA
                    $(".info_queue_item_"+u['id']+".upload_total").text(u['total'].toFixed(1));
                    $(".info_queue_item_"+u['id']+".upload_done").text(u['done'].toFixed(1));
                    $(".info_queue_item_"+u['id']+".done_percent").text(u['done_percent'].toFixed(1));
                    $(".info_queue_item_"+u['id']+".current_file").text(u['current_file']);
                    $(".info_queue_item_"+u['id']+".current_speed").text(u['speed'].toFixed(1));
                    $(".info_queue_item_"+u['id']+".eta_str").text(u['eta_str']);
                    $(".info_queue_item_"+u['id']+".added").text(u['added']);
                    $(".info_queue_item_"+u['id']+".estimate_start").text(u['estimate_start']);
                    $(".info_queue_item_"+u['id']+".end_time_str").text(u['end_time_str']);
                }
            }
        }
    })
}

$(document).ready(function(){
    set_part_focus($(".part"));
    $(".part").click(function() {
        set_part_focus($(this));
    })

    $('#submit_button').click(function(){
        get_data();        
    })

});
