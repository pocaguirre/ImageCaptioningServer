$(document).ready(function(){
    $("#submit_button").on('click', function(){
        let answers = {};
        $(".form-range").each(function() {
            answers[$(this).attr('id')] = $(this).val();
        });
        $.post("/special/rating_submit", {
                data: JSON.stringify(answers)
            }, function(data){
            window.location.replace(data.href);
        });
    });
});
