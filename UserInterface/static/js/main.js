// ============================================================================
// create question set and state to go through the questions
// ============================================================================
var questions = new Array();
var worker_obj = new Object();
var state = -1;
jQuery.support.cors = true;

$(window).load(function(){
    if (mturk === 'sandbox' || mturk === 'mturk') {
        addDialog();
        workerID = turkGetParam("workerId");
        assignID = turkGetParam("assignmentId");
    }
    let dialog_modal = $("#dialog-modal" );
    worker_obj.id = workerID
    worker_obj.assignmentID = assignID
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
    $.post( "/get_task", { workerID: workerID,
                                                                        assignID: assignID}, function( data ) {
        // Set Images
        var im_urls = data.images;
        // Set HTML
        $( "#main-body" ).load( data.html, function(){
           // Import JS and execute
            $.getScript( data.js, function() {
                function check_completed() {
                    let empty_input = false;
                    // CHECK DEMOGRAPHIC FORM INPUTS ARE FILLED
                    if (
                        $("[name='age-input']").val() === "" ||
                        $("[name='education-radio']:checked").length === 0 ||
                        $("[name='glasses-radio']:checked").length === 0 ||
                        $("[name='colorblind-radio']:checked").length === 0
                    ){
                        empty_input = true;
                    }
                    if(Cookies.get('demographics_finished') === "True"){
                        empty_input = false;
                    }
                    if (empty_input === false){
                        // CHECK INSTRUCTIONS ARE CLICKED
                        check_all_checks();
                    }
                }

                render_header_button(im_urls);
                initialize_images(im_urls);
                $('#next').on('click', function(){next();});
                $('#prev').on('click', function(){prev();});
                $("#start-btn").on('click', function (){
                    worker_obj['age-input'] = $("[name='age-input']").val();
                    worker_obj['education-radio'] = $("[name='education-radio']:checked").val();
                    worker_obj["glasses-radio"] = $("[name='glasses-radio']:checked").val();
                    worker_obj["colorblind-radio"] = $("[name='colorblind-radio']:checked").val();
                    start();
                })
                $("#submitButton").on('click', function (){submit_function();});
                var els = document.getElementsByClassName('instruction-check');
                for (var i = 0; i < els.length; i++) {
                    els[i].onclick = check_completed;
                }
                $('#demographics-form input').on("click", check_completed);
            });
            if (mturk === 'sandbox' || mturk === 'mturk') {
                turkSetAssignmentID();
            }
        });
    }, "json");
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
    var link_to_next;
    $.post('/submit_data',
        {
            answer: $('#ans').val(),
            assignmentID: assignID,
            workerID: workerID,
            mturk: mturk,
            demographics: JSON.stringify(worker_obj),
            difficulty: $("[name='difficulty_radio']:checked").val(),
            length: $("[name='length_radio']:checked").val(),
            comments: $('#final_comments').val()
        },
        function(data) {
            link_to_next = data.link;
            Cookies.set('demographics_finished', 'True');
            if (mturk === 'sandbox' || mturk === 'mturk') {
                $("#mturk_form").submit(); // Submit the form
            } else {
                Cookies.set('assignment_finished', 'True');
            }
            let dialog_task = $("#dialog-task");
            if (link_to_next === "done") {
                dialog_task.dialog({
                    autoOpen: false,
                    height: 250,
                    buttons: {
                        'YOU ARE DONE!': function() {
                            $(this).dialog("close");
                            $(this).text("");
                        }
                    }
                });
            } else {
                dialog_task.dialog({
                    autoOpen: false,
                    height: 250,
                    buttons: {
                        'Next HIT': function() {
                            $(this).dialog("close");
                            $(this).text("");
                            window.location.href = link_to_next;
                        }
                    }
                });
            }
            dialog_task.text("Thank you for completing this HIT");
            dialog_task.dialog('open');
        }, "json"
    );
}


// ===========================================================
// disable cut and paste on input text
// ===========================================================
$(document).ready(function(){
  $(document).on("cut copy paste","#description",function(e) {
      e.preventDefault();
  });
 });