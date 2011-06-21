$(document).ready(function(){
    //alert("bla");
    /*
$("#do_connect").change(function(){
        //alert(this.checked);
        if (this.checked)
        {
            //alert("true");
            $("#active").val("1");
        }
        else
        {
            //alert("no");
            $("#active").val("0");
        }
        $("#remotestorages_list").submit();
    });
*/
    $(".form").slideToggle();
    $(".show-form").click(function(){
        $(".form").slideToggle();
        return false;
    });
});