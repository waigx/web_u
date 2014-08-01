$(document).ready(
    function() {
        $("#test_form").submit(function (event) {
            event.preventDefault();
            var formData = $(this).serialize();
            var url = $(this).attr("action");
            $.ajax(
                {
                    url: url,
                    type: "POST",
                    data: formData,
                    success: function (data, textStatus, jqXHR) {
                        //data: return data from server
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        //if fails
                    }
                });
        });
    });