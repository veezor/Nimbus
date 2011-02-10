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
    
});