STATIC_ROOT = "https://imagecaptioningicl.azurewebsites.net/static";

// ============================================================================
// create question set and state to go through the questions
// ============================================================================
var questions = new Array();
var state = -1;
var init_time = $.now();

// change im_urls to your images
let instruction_im_path = STATIC_ROOT + "/images/dog.jpg";
let instruction_im = new Image();
instruction_im.src = instruction_im_path;
var im_urls = [ STATIC_ROOT + "/images/dog.jpg",
                STATIC_ROOT + "/images/cat.jpg",
                STATIC_ROOT + "/images/dog.jpg",
                STATIC_ROOT + "/images/cat.jpg",
                STATIC_ROOT + "/images/dog.jpg"];

// ============================================================================
// initialize images
// ============================================================================
for (i=0; i < im_urls.length; i++){
    var im = new Image();
    var q = new Object();
    im.src = im_urls[i];
    q.im = im;
    q.ans = '';
    q.done = false;
    q.seen = false; // TODO: add button to see image, then start counter, then show image, then empty canvas
    // TODO: add fields for identifying images here
    questions.push(q);
}

// ============================================================================
// page onload
// ============================================================================
$(window).load(function(){
    render_header_button(im_urls);
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
    $('#next').on('click', function(){next();});
    $('#prev').on('click', function(){prev();});
    $("#see-image").on("click", function(){see_image_btn();});
    $("#see-image-instruction").on("click", function(){see_image_instruction_btn();});
    $("#start-btn").on('click', function (){start();})
    var els = document.getElementsByClassName('instruction-check');
    for (var i = 0; i < els.length; i++) {
      els[i].onclick = check_all_checks;
    }

})

// ================================================================
// function to control next and previous question
// ===============================================================
function next(){
    let ans = $('#description').val();
    if (ans.length > 0){
        var q = questions[state];
        // store user input
        q.ans = ans;
        if (!check_correct(q)){
            return -1;
        }
    }
    if (state < questions.length - 1){
        state += 1;
        render_question(state);
        update_header_buttons(state);
    }else{
        if (!finish()){
            return -1;
        }
    }
}

function prev(){
    let ans = $('#description').val();
    if (ans.length > 0){
        var q = questions[state];
        // store user input
        q.ans = ans;
        if (!check_correct(q)){
            return -1;
        }
    }
    if (state > 0){
        state -= 1;
        render_question(state);
    } else if (state === 0){
        state -= 1;
    }
    update_header_buttons(state);
}

function update(event){
    var button = event.currentTarget;
    if (button.disabled){
        return -1;
    }

    if (0 <= state && state < questions.length) {
        let ans = $('#description').val();
        if (ans.length > 0){
            var q = questions[state];
            // store user input
            q.ans = ans;
            if (!check_correct(q)){
                return -1;
            }
        }
    }

    var id = button.id;
    if (id === "inst"){
        state = -1
        $("#images").prop('hidden', true);
        $("#instructions").prop('hidden', false);
        $("#finish").prop('hidden', true);
    } else if (id === "fin"){
        $("#images").prop('hidden', true);
        $("#instructions").prop('hidden', true);
        $("#finish").prop('hidden', false);
    } else {
        $("#images").prop('hidden', false);
        $("#instructions").prop('hidden', true);
        $("#finish").prop('hidden', true);
        state = parseInt(id[id.length - 1]) -1;
        render_question(state);
    }
    update_header_buttons(state);
}

function start(){
    state = 0;
    $("#images").prop('hidden', false);
    $("#instructions").prop('hidden', true);
    $("#finish").prop('hidden', true);
    render_question(state);
    update_header_buttons(state);
    $( ".header-btn" ).each(function( index ) {
        if (index !== 0 && index !== questions.length + 1) {
            $(this).prop("disabled", false);
        }
    });
}

function finish(){
    for (i=0; i < questions.length; i++){
        if (questions[i].done === false){
            render_dialog(9);
            return false;
        }
    }
    $("#images").prop('hidden', true);
    $("#instructions").prop('hidden', true);
    $("#finish").prop('hidden', false);
    state += 1;
    update_header_buttons(state);
    $("#dialog-confirm" ).dialog('open');
}

function check_correct(question){
    if (question.ans.split(' ').length < 8){
        render_dialog(7);
        return false;
    } else {
        question.done = true;
        return true;
    }
}

function check_all_checks(){
    if ($(".instruction-check:checked").length > 6) {
        $("#start-btn").prop("disabled", false);
    }
}
// ===============================================================
// rendering question, image, and dialog
// ==============================================================
function render_header_button(im_urls){
    $( "#button-header-group" ).append(`<button type="button" id="inst" class="header-btn btn btn-info">Instructions</button>`);
    for (var i=1; i <= im_urls.length; i++){
        $( "#button-header-group" ).append(`<button type="button" id="image-${i}" class="header-btn btn btn-outline-secondary" disabled>Image ${i}</button>`);
    }
    $( "#button-header-group" ).append(`<button type="button" id="fin" class="header-btn btn btn-outline-secondary" disabled>Finish</button>`);
    $(".header-btn").on('click', function(event){
        event.stopPropagation();
        event.stopImmediatePropagation();
        update(event);
    });
}

function render_question(idx){
    q = questions[idx];
    $('.state-button').show();
    if (q.seen) {
        $("#see-image-div").prop('hidden', true);
        $("#already-seen").prop('hidden', false);
    } else {
       $("#see-image-div").prop('hidden', false);
       $("#already-seen").prop('hidden', true);
    }
    $('#description').show();
    $('#description').css('width', 480);
    $('#description').css('height', 150);
    $('#description').val(q.ans);
}

function see_image_btn(){
    $("#see-image-div").prop('hidden', true);
    let countdown = $("#countdown")
    countdown.prop('hidden', false);
    countdown.countdown360({
      radius      : 60.5,
      seconds     : 3,
      strokeWidth : 15,
      fillStyle   : '#0276FD',
      strokeStyle : '#003F87',
      fontSize    : 50,
      fontColor   : '#FFFFFF',
      autostart: false,
      onComplete  : function () {
          $("#countdown").prop('hidden', true);
          q = questions[state];
          q.seen = true;
          render_im(q.im);
          setTimeout(() => {  clear_im(); }, 500);
      }
    }).start();
}


function see_image_instruction_btn(){
    $("#see-image-div-instruction").prop('hidden', true);
    let countdown = $("#countdown-instruction")
    countdown.prop('hidden', false);
    countdown.countdown360({
      radius      : 60.5,
      seconds     : 3,
      strokeWidth : 15,
      fillStyle   : '#0276FD',
      strokeStyle : '#003F87',
      fontSize    : 50,
      fontColor   : '#FFFFFF',
      autostart: false,
      onComplete  : function () {
          $("#countdown-instruction").prop('hidden', true);
          render_im(instruction_im, canvas="#canvas-instruction");
          setTimeout(() => {  clear_im(canvas="#canvas-instruction"); }, 500);
      }
    }).start();
}

function clear_im(canvas="#canvas"){
    var c = $(canvas)[0];
    var ctx = c.getContext("2d");
    ctx.clearRect(0, 0, c.width, c.height);
}

function render_im(im, canvas="#canvas"){
    im.height = im.height * 480 / im.width;
    im.width = 480;
    var c = $(canvas)[0];
    if (im.width > im.height){
        c.width =  480;
        c.height = im.height * 480 / im.width;
    }else{
        c.height = 360;
        c.width = im.width * 360 / im.height
    }
    var ctx=c.getContext("2d");
    ctx.drawImage(im, 0, 0, c.width, c.height);
}

function update_header_buttons(activeIdx){
    $( ".header-btn" ).each(function( index ) {
        let cl;
        if (index === 0) {
            $(this).removeClass("btn-info").addClass("btn-outline-info");
            if (index === activeIdx + 1){
                $(this).removeClass("btn-outline-info").addClass("btn-info");
            }
        } else if (index > questions.length){
            $(this).removeClass("btn-success").addClass("btn-outline-secondary");
            if (index === activeIdx + 1){
                $(this).removeClass("btn-outline-secondary").addClass("btn-success");
            }
        } else {
            $(this).removeClass("btn-secondary btn-outline-secondary btn-success btn-outline-success");
            if (index === activeIdx + 1){
                if ( index - 1 < questions.length && questions[index - 1].done){
                    $(this).addClass("btn-success");
                } else {
                    $(this).addClass("btn-secondary");
                }
            } else {
                if ( index - 1 < questions.length && questions[index - 1].done){
                    $(this).addClass("btn-outline-success");
                } else {
                    $(this).addClass("btn-outline-secondary");
                }
            }
        }
    });
    for (i=0; i < questions.length; i++){
        if (questions[i].done === false){
            return;
        }
    }
    $("#fin").prop("disabled", false);
}

function render_dialog(idx){
    if (idx==1){
        var text = 'Do not describe unimportant details.';
    }else if(idx == 2){
        var text = 'Do not describe things that might have happened in the future or past.';
    }else if(idx == 3){
        var text = 'Do not describe what a person might say.';
    }else if(idx == 4){
        var text = 'Do not give people proper names.';
    }else if(idx == 5){
        var text = 'This is the BEST sentence! Please apply the same rule to describe following 3 images.';
    }else if(idx == 6){
        var text = 'Please includes more details.';
    }else if(idx==7){
        var text = 'Please enter more than 8 words.';
    }else if(idx==8){
        var text = 'Error occured when submitting the form, please try again.';
    }else if (idx==9){
        var text = "Please complete all descriptions.";
    }
    $("#dialog-modal" ).text(text);
    $("#dialog-modal" ).dialog('open');
}

function getAnswers(){
    var answers = [];
    for (var i=0; i<questions.length; i++){
        answers.push({
            description: questions[i].ans,
            im_url: im_urls[i]
        });
    }
    return answers;
}

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