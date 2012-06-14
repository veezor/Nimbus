// TEMPO DE REFRESH EM MILISEGUNDOS
REFRESH_TIME = 5000;

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
            if (j['uploads'].length == 0) {
                $("#empty_content").show();
                $("#full_content").hide();
            } else {
                $("#empty_content").hide();
                $("#full_content").show();                
            }
            $("#upload_done").text(j['upload_done'].toFixed(1));
            $("#upload_total").text(j['upload_total'].toFixed(1));
            var percent_done = (100 * j['upload_done'] / j['upload_total'])
            $("#percent_done").text(percent_done.toFixed(1));
            $("#current_speed").text(j['current_speed'].toFixed(1));
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
                        if ($(".part").length > 0) {
                            $("#" + $(".part")[0].id).addClass("selected");
                            $("#info_" + $(".selected")[0].id).show();
                        }
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
                    if ("queue_item_" + u['id'] == blocks_list[item]) {
                        item_exists = true;
                    }
                }
                if (item_exists == false) {
                    var new_block = '<div id="queue_item_'+u['id']+'" onClick="set_part_focus($(this));" class="part"><div class="name_block"><span>'+u['name']+'</span></div><div class="done_part_block"><div class="done_part queue_item_'+u['id']+'" style="width: '+u['done_percent']+'%;"></div></div><div class="icon info_queue_item_'+u['id']+'"></div></div>';
                    var new_info_block  = '' +
                        '<div class="upload_info" id="info_queue_item_'+u['id']+'" style="display: none;">' +
            				'<table>' +
            					'<tbody>' +
            						'<tr><td>'+gettext('Procedures:')+'</td><td><span class="upload_name info_queue_item_'+u['id']+'"></span></td></tr>' +
            						'<tr><td>'+gettext('Completed:')+'</td><td><span class="upload_done info_queue_item_'+u['id']+'"></span> de <span class="upload_total info_queue_item_'+u['id']+'"></span> MB (<span class="done_percent info_queue_item_'+u['id']+'"></span>%)</td></tr>' +
            						'<tr><td>'+gettext('Current volume:')+'</td><td><span class="current_file info_queue_item_'+u['id']+'"></span></td></tr>' +
            						'<tr><td>'+gettext('Transfer rate:')+'</td><td><span class="current_speed info_queue_item_'+u['id']+'"></span> kB/s</td></tr>' +
            						'<tr><td>'+gettext('Estimated time left:')+'</td><td><span class="eta_str info_queue_item_'+u['id']+'"></span></td></tr>' +
            						'<tr><td>'+gettext('Added to queue at:')+'</td><td><span class="added info_queue_item_'+u['id']+'"></span></td></tr>' +
            						'<tr><td>'+gettext('Start in:')+'</td><td><span class="estimate_start info_queue_item_'+u['id']+'"></span></td></tr>' +
            						'<tr><td>'+gettext('Conclusion estimated time:')+'</td><td><span class="end_time_str info_queue_item_'+u['id']+'"></span></td></tr>' +
            					'</tbody>' +
            				'</table>' +
            				'<div class="progress_bar">' +
            					'<div class="done_bar info_queue_item_'+u['id']+'"></div>' +
            				'</div>' +
            			'</div>'
            		if (j['uploads'].length == 1 || $(".part").length == 0) {
            		    $("#fullbar").append(new_block);
            		    $("#upload_info_box").append(new_info_block);
            		} else if (i == 0) {
                        $(new_block).insertBefore("#" + $(".part")[0].id)
                        $(new_info_block).insertBefore("#info_" + $(".part")[0].id)
                    } else {
                        $(new_block).insertAfter("#queue_item_" + j['uploads'][i-1]['id']);                        
                        $(new_info_block).insertAfter("#info_queue_item_" + j['uploads'][i-1]['id']);                        
                    }
                }
            }
            // FIM DE VERIFICA SE EXISTE UM NOVO BLOCO E O CRIA
            for (var i = 0; i < j['uploads'].length; i++) {
                u = j['uploads'][i];
                // REDIMENSIONA OS BLOCOS E MOVE A SETA
                $(".info_queue_item_"+u['id']+".done_bar").animate({"width": u['done_percent'] + "%"}, "slow");
                $(".queue_item_"+u['id']+".done_part").animate({"width": u['done_percent'] + "%"}, "slow");
                if ($("#queue_item_" + u['id']).width() != u['block_width']) {
                    $(".icon").fadeOut("slow")
                    $("#queue_item_" + u['id']).animate({"width": u['block_width'] + "px"}, "slow", function(){
                        if ($(this).hasClass("selected") == true) {
                            var new_arrow_position = $(this)[0].offsetLeft + ($(this)[0].offsetWidth / 2) - 6;
                            $("#marker").animate({"left": new_arrow_position+"px"}, "slow");
                            $(".icon").fadeIn("slow")
                        }
                    })
                }
                // FIM DE REDIMENSIONA OS BLOCOS E MOVE A SETA
                // MUDA O ICONE INDICATIVO DE UPLOAD
                var status_icon = "no_icon"
                if (u['done'] > 0) {
                    status_icon = "upload_icon";
                    if (u['speed'] == 0) {
                        status_icon = "stalled_icon";
                    }
                }
                if ($(".icon.info_queue_item_"+ u['id']).hasClass(status_icon) == false) {
                    $(".icon.info_queue_item_"+ u['id']).removeClass("upload_icon stalled_icon no_icon");
                    $(".icon.info_queue_item_"+ u['id']).addClass(status_icon)
                }
                // FIM DE MUDA O ICONE INDICATIVO DE UPLOAD
                $(".info_queue_item_"+u['id']+".upload_name").text(u['name']);
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
    })
    var t=setTimeout("get_data()",REFRESH_TIME)
}

$(document).ready(function(){
    if ($(".part").length > 0) {
        set_part_focus($(".part"));        
    }

    $('#submit_button').click(function(){
        get_data();        
    })
    var t=setTimeout("get_data()",REFRESH_TIME)
});
