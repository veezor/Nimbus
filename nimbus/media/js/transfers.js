$(document).ready(function(){
    $(".part").click(function() {
        var queue_id = $(this)[0]
        var arrow_position = queue_id.offsetLeft + (queue_id.offsetWidth / 2);
        $("#marker").animate({"left": arrow_position+"px"}, "slow", function(){
            $(".upload_info").hide();
            $("#info_" + queue_id.id).show();            
        });
    })
});
