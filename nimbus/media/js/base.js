$(document).ready(function(){
    // Accordeon for procedure history
    $(".hide").slideUp();
    $('.job_line').click(function(){
        $(".hide").slideUp();
        var next = $(this).next();
        if (next.css('display') == 'none')
            next.slideDown();
        else
            next.slideUp();
    });
    $('.job_line').mouseover(function(){
        $(this).addClass('over');
    });
    $('.job_line').mouseout(function(){
        $(this).removeClass('over');
    });
    $('#about_buttom').click(function(){
        $.facebox(function(){
            $.facebox({ ajax: "/base/about"});
        });
        return false;
    });
});
