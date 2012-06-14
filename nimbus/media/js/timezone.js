$(document).ready(function() {
    function getAreaChoices() {
        $.ajax({
            type: "POST",
            url: $("#area_request").val(),
            dataType: "json",
            data: {country: $('[name=country]').val()},
            success: function(data, textStatus){
                $("select#id_area").empty();
                $.each(data, function(i, item){
                    $("select#id_area").append(
                        '<option value="'+item+'" selected="selected">'+item+'</option>'
                    );
                });
                $("select#id_area").change();
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert(gettext("Error: Unable to get the list of time zones."));
                this; // the options for this ajax request
            }
        });
    }
    
    $("select#id_country").bind("change", getAreaChoices);
});