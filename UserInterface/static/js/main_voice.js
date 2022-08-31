
$(window).load(function(){
    let dialog_modal = $("#dialog-modal" );
    dialog_modal.dialog({
          autoOpen: false,
          height: 250,
          modal: true,
            buttons: {
            'ok':function(){
                $( this ).dialog( "close" );
            },
        }
        });
    dialog_modal.hide();
    
    $("#start-btn").on('click', function (){
        worker_obj['email-input'] = $("[name='email-input']").val();
        worker_obj['age-input'] = $("[name='age-input']").val();
        worker_obj['race-input'] = get_multiple_choice_answer("race-checkbox");
        worker_obj['ethnicity-input'] = get_multiple_choice_answer("ethnicity-checkbox");
        worker_obj['gender-input'] = get_multiple_choice_answer("gender-checkbox");
        worker_obj['education-radio'] = $("[name='education-radio']:checked").val();
        worker_obj['english-radio'] = $("[name='english-radio']:checked").val();
        worker_obj["glasses-radio"] = $("[name='glasses-radio']:checked").val();
        worker_obj['lenses-radio'] = $("[name='lenses-radio']:checked").val();
        worker_obj["colorblind-radio"] = $("[name='colorblind-radio']:checked").val();
        $.post( "/voice/get_images", { workerID: worker_obj['email-input']}, function( images ) {
            // Set Images
            var im_urls = images;
            render_header_button(im_urls);
            initialize_images(im_urls);
            $('.next').on('click', function(){next();});
            start();
        }, "json");
    })
    $("#submitButton").on('click', function (){submit_function();});
    $('#demographics-form input').on("click", check_completed);
    $('#calibrating').on("click", start_calibration);
    $("#startRecord").on('click', start_record);
    $("#stopRecord").on("click", stop_record);
    $("#description").on("keydown", has_words);
})

// ===========================================================
// add dialog for the web page
// ===========================================================
function addDialog(){
    $( "#dialog-confirm" ).dialog({
      autoOpen: false,
      resizable: false,
      height:140,
      modal: true,
      buttons: {
        "Yes": function() {
          $( this ).dialog( "close" );
          $("#ans").val(JSON.stringify(getAnswers()));
          // $('#mturk_form').submit();
        },
        Cancel: function() {
          $( this ).dialog( "close" );
        }
      }
    });
    $( ".ui-dialog" ).css('position', 'absolute');
}

function get_data(){
    var formData = new FormData();
    formData.append("workerID", worker_obj['email-input']);
    formData.append("condition", condition);
    formData.append("medium", medium);
    formData.append("assignmentID", assignmentID);
    formData.append("demographics", JSON.stringify(worker_obj));
    formData.append("calibrations", JSON.stringify(calibrations));
    ans_obj = getAnswers();
    answers_dict = ans_obj[0];
    blobs = ans_obj[1];
    formData.append("answers", JSON.stringify(answers_dict));
    for(var i=0; i < blobs.length; i +=1){
        formData.append(blobs[i]['fname'], blobs[i]['blob']);
    }
    return formData
}

function submit_function(){
    ajaxData = get_data();
    $.ajax({type: 'POST',
            url: '/voice/submit',
            data: ajaxData,
            processData: false,
            contentType: false,
            beforeSend: function(){
                $(".lds-spinner").prop("hidden", false);
                $("#submitButton").prop("disabled", true);
            },
            complete: function(){
                $(".lds-spinner").prop("hidden", true);
            },
            success: function(data) {
            if (data.success === true){
                success_dialog();
            } else {
                error_dialog();
            }
        },
        crossDomain:true
    });
}

// ===========================================================
// RUN DIALOG
// ===========================================================
function success_dialog(){
    let dialog_task = $("#dialog-task");
    dialog_task.dialog({
        autoOpen: false,
        height: 250,
        buttons: {
            "SUCCESS!": function() {
                $(this).dialog("close");
                $(this).text("");
            }
        }
    });
    dialog_task.text("Thank you for completing this study!");
    dialog_task.dialog('open');
}

function error_dialog(){
    let dialog_task = $("#dialog-error");
    dialog_task.dialog({
        autoOpen: false,
        height: 250,
        buttons: {
            "ERROR!": function() {
                $(this).dialog("close");
                $(this).text("");
            }
        }
    });
    dialog_task.text("There was an unexpected error. Please submit again");
    dialog_task.dialog('open');
}

// ===========================================================
// CHECK DEMOGRAPHIC FORM INPUTS ARE FILLED
// ===========================================================
function check_completed() {
    let empty_input = true;
    if (
        $("[name='email-input']").val() !== "" &&
        $("[name='age-input']").val() !== "" &&
        $("[name='education-radio']:checked").length !== 0 &&
        $("[name='english-radio']:checked").length !== 0 &&
        $("[name='glasses-radio']:checked").length !== 0 &&
        $("[name='lenses-radio']:checked").length !== 0 &&
        $("[name='colorblind-radio']:checked").length !== 0
    ){
        empty_input = false;
    }
    if (empty_input === false){
        // CHECK INSTRUCTIONS ARE CLICKED
        $(".start-btn").prop("disabled", false);
    }
}

// ===========================================================
// disable cut and paste on input text
// ===========================================================
$(document).ready(function(){
  $(document).on("cut copy paste","#description",function(e) {
      e.preventDefault();
  });
 });


// ===========================================================
// get multiple choice responses
// ===========================================================
function get_multiple_choice_answer(element_name) {
    var checkboxes = document.getElementsByName(element_name);
    var answers = [];
    for(var i = 0; i < checkboxes.length; i++){
        if(checkboxes[i].checked){
            answers.push(checkboxes[i].value);
        }
        else if(checkboxes[i].type === "text" && checkboxes[i].value !== ""){
            answers.push(checkboxes[i].value)
        }
    }
    return answers
}