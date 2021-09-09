$(document).ready(function(){
    if(Cookies.get('email')){
        $("#email").val(Cookies.get('email'));
        $("#emailConfirm").val(Cookies.get('email'));
        $("#firstname").val(Cookies.get('fName'));
        $("#lastname").val(Cookies.get('lName'));
    }
    $("#info-form").validate({
        rules: {
            email: 'required',
            emailConfirm: {
                equalTo: '#email'
            },
            firstname: 'required',
            lastname: 'required'
        }
    })
    $("#submit_button").on('click', function(){
        let answers = {};
        $(".form-range").each(function() {
            answers[$(this).attr('id')] = $(this).val();
        });
        let email = $('#email').val()
        let fName = $("#firstname").val()
        let lName = $('#lastname').val()
        Cookies.set('email', email);
        Cookies.set('fName', fName);
        Cookies.set('lName', lName);
        $.post("/rating_submit", {
                email: email,
                first_name: fName,
                last_name: lName,
                data: JSON.stringify(answers)
            }, function(data){
            window.location.replace(data.href);
        });
    });
});
