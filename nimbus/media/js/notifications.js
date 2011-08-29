$(document).ready(function(){
    $.ajax({
        type: "POST",
        url: "/base/notifications/",
        dataType: "json",
        success: function(notes) {
            for (var n = 0; n < notes.length; n++) {
                $("#notifier").append('<div class="noteblock" id="note_'+notes[n]['id']+'"><span class="notebox"><a onClick="ack('+notes[n]['id']+')" href="' +notes[n]['link']+ '">' + notes[n]['message'] + '</a></span><span class="ack" onClick="ack('+notes[n]['id']+')"></span></div>')
        	};
        }
    });
});
function ack(id) {    
    $.ajax({
        type: "GET",
        url: "/base/ack_notification/",
        data: "id="+ id,
        dataType: "json",
        success: function(e) {
            console.log(e);
        }
    })
    $("#note_" + id).remove()
    return true;
}