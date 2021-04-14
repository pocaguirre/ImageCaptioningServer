// ============================================================================
// create question set and state to go through the questions
// ============================================================================
var questions = new Array();
var state = -1;
var init_time = $.now();

$(window).load(function(){
    if (mturk) {
        $("#dialog-modal" ).dialog({
          autoOpen: false,
          height: 250,
          modal: true,
            buttons: {
            'ok':function(){
                $( this ).dialog( "close" );
            },
        }
        });
        addDialog();
        $( "#dialog-modal" ).hide();
        workerID = turkGetParam("workerId");
        assignID = turkGetParam("assignmentId");
    }
    $.post( "https://imagecaptioningicl.azurewebsites.net/get_task", { workerID: workerID,
                                                                        assignID: assignID}, function( data ) {
        // Set Images
        var im_urls = data.images;
        // Set HTML
        $( "#main-body" ).load( data.html );
        // Import JS and execute
        $.getScript( data.js, function() {
            render_header_button(im_urls);
            initialize_images(im_urls);
            $('#next').on('click', function(){next();});
            $('#prev').on('click', function(){prev();});
            $("#start-btn").on('click', function (){start();})
            var els = document.getElementsByClassName('instruction-check');
            for (var i = 0; i < els.length; i++) {
                els[i].onclick = check_all_checks;
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

// ===========================================================
// disable cut and paste on input text
// ===========================================================
$(document).ready(function(){
  $(document).on("cut copy paste","#description",function(e) {
      e.preventDefault();
  });
 });