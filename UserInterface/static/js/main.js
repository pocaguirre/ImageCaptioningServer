
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
        $("#start-btn").prop('disabled', true);
        worker_obj['email-input'] = $("[name='email-input']").val();
        worker_obj['age-input'] = $("[name='age-input']").val();
        worker_obj['education-radio'] = $("[name='education-radio']:checked").val();
        worker_obj["glasses-radio"] = $("[name='glasses-radio']:checked").val();
        worker_obj["colorblind-radio"] = $("[name='colorblind-radio']:checked").val();
        $.post( "/inperson/get_images", { workerID: worker_obj['email-input']}, function( images ) {
            // Set Images
            if (typeof im_urls !== 'undefined'){
                return;
            }
            var im_urls = images;
            render_header_button(im_urls);
            initialize_images(im_urls);
            $('#next').on('click', function(){next();});
            start();
        }, "json");
    })
    $("#submitButton").on('click', function (){
        $("#start-btn").prop('disabled', true);
        submit_function();}
        );
    var els = document.getElementsByClassName('instruction-check');
    for (var i = 0; i < els.length; i++) {
        els[i].onclick = check_completed;
    }
    $('#demographics-form input').on("click", check_completed);
    $('#calibrating').on("click", start_calibration);
    $("#description").on("keypress", has_words);
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


function submit_function(){
    $("#ans").val(JSON.stringify(getAnswers()));
    $.post('/inperson/submit',
        {
            answer: $('#ans').val(),
            workerID: worker_obj['email-input'],
            condition: condition,
            assignmentID: assignmentID,
            demographics: JSON.stringify(worker_obj),
            calibrations: JSON.stringify(calibrations)
        },
        function(data) {
            if (data.success === true){
                success_dialog();
            } else {
                error_dialog();
            }
        }, "json"
    );
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
    dialog_task.text("Thank you for completing this HIT");
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
        $("[name='glasses-radio']:checked").length !== 0 &&
        $("[name='colorblind-radio']:checked").length !== 0
    ){
        empty_input = false;
    }
    if (empty_input === false){
        // CHECK INSTRUCTIONS ARE CLICKED
        check_all_checks();
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