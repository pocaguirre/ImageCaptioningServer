$(document).ready(function(){
    let inputs = [];
    $(".form-range").on('click', function(){
        let id = $(this).attr('id');
        if(!inputs.includes(id)){
            inputs.push(id);
        }
        if(inputs.length === 18){
            $("#submit_button").prop("disabled", false);
        }
    });

    $("#submit_button").on('click', function(){
        let answers = {};
        $(".form-range").each(function() {
            answers[$(this).attr('id')] = $(this).val();
        });
        $.post("/rating_submit", {
                worker_id: Cookies.get('worker_id'),
                rating_id: Cookies.get('rating_id'),
                data: JSON.stringify(answers)
            }, function(data){
            window.location.replace(data.href);
        });
    });
});
