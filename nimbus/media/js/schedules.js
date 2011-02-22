$(document).ready(function(){
    $('.schedule_activate').change(function(){
        _checked = $(this).attr('checked');
        _class = $(this).attr('id');
        if (_checked) {
            $('.' + _class).addClass('active');
        } else {
            $('.' + _class).removeClass('active');
        }
    });
    $('.schedule_activate').change();
});