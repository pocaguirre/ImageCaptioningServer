// ============================================================================
// create question set and state to go through the questions
// ============================================================================
var worker_obj = new Object();
var calibrations = new Array();
var state = -1;
var image_index = 0;
jQuery.support.cors = true;
var questions = new Array();

var start_time = new Date().getTime();

var WINDOW_WIDTH = $(window).width();

var canvas = $("#canvas_speech");

$(document).ready(function(){
    $("#instructions_written").prop("hidden", true);
    canvas = $("#canvas_speech");
   });


// ============================================================================
// initialize images SPEECH -> WRITTEN
// ============================================================================
function initialize_images(im_urls){
    // Do speech
    for (var i=0; i < im_urls.length; i++){
        var im = new Image();
        var q = new Object();
        im.src = im_urls[i];
        q.im = im;
        q.done = false;
        q.time = 0;
        q.start_time = 0;
        q.end_time = 0;
        questions.push(q);
    }

}
// ============================================================================
// AUDIO recording
// ============================================================================


function renderAudioError(message) {
    const main = document.querySelector('error_div');
    main.innerHTML = `<div class="error"><p>${message}</p></div>`;
  }

var audioChunks;
var recorder;

function start_record() {
  let startRecord = $("#startRecord");
  let stopRecord = $("#stopRecord");
  startRecord.prop('disabled', true);
  stopRecord.prop('disabled', false);
  // This will prompt for permission if not allowed earlier
  navigator.mediaDevices.getUserMedia({audio:true})
    .then(stream => {
      audioChunks = []; 
      recorder = new MediaRecorder(stream);
      recorder.ondataavailable = e => {
        audioChunks.push(e.data);
        if (recorder.state == "inactive"){
          questions[image_index].ans = new Blob(audioChunks,{type:'audio/webm'});
          recordedAudio.src = URL.createObjectURL(questions[image_index].ans);
          recordedAudio.controls=true;
          recordedAudio.autoplay=false;
       }
      }
    recorder.start();  
    })
    .catch(e=>console.log(e));
}
function stop_record() {
  questions[image_index].done = true;
  let startRecord = $("#startRecord");
  let stopRecord = $("#stopRecord");
  startRecord.prop('disabled', false);
  stopRecord.prop('disabled', true);
  $(".next").prop("disabled", false);
  recorder.stop();
}

function empty_audio(){
    recordedAudio.src = "";
    recordedAudio.controls = false;
}
// ================================================================
// function to control next and previous question
// ===============================================================

function has_words(){
    // returns true if text are has more than one word
    let text = $("#description").val()
    if (text.split(/\s+/).length > 1){
        $(".next").prop("disabled", false);
        return
    }
    $(".next").prop("disabled", true);
}

// ================================================================
// function to control next and previous question
// ===============================================================
function next(){
    if (state === -1) {
        // Was calibrating, start q 0
        $("#images_speech").prop('hidden', false);
        $("#images_written").prop('hidden', true);
        state += 1;
        render_question(image_index);
        update_header_buttons(state);
    }
    else if (state >= 0 && state < 4) {
        // Was q state, start q state + 1
        // let ans = $('#description').val();
        // if (!check_correct(ans, image_index)){
        //     return -1;
        // }
        record_answers(questions[image_index].ans, image_index);
        state += 1;
        image_index += 1;
        render_question(image_index);
        update_header_buttons(state);
        empty_audio();
    }
    else if (state === 4) {
        // Was question 4, instructions 2
        state += 1;
        record_answers(questions[image_index].ans, image_index);
        empty_audio();
        $("#circles").prop('hidden', true);
        $("#images_speech").prop('hidden', true);
        $("#images_written").prop('hidden', true);
        $("#instructions_speech").prop('hidden', true);
        $("#instructions_written").prop('hidden', false);

        $("#finish").prop('hidden', true);
        update_header_buttons(state);
        $(".start-btn").on('click', next);
        $(".start-btn").prop('disabled', true);
        canvas = $("#canvas_written")
    }    
    else if (state === 5) {
        // Was instructions 2, start calibrating
        // let ans = $('#description').val();
        // if (!check_correct(ans, state)){
        //     return -1;
        // }
        state += 1;
        $("#circles").prop('hidden', false);
        $("#images_speech").prop('hidden', true);
        $("#images_written").prop('hidden', true);
        $("#instructions_speech").prop('hidden', true);
        $("#instructions_written").prop('hidden', true);
        $("#finish").prop('hidden', true);
        update_header_buttons(state);
    }
    else if (state === 6){
        // Was calibrating, start q 5
        $("#images_speech").prop('hidden', true);
        $("#images_written").prop('hidden', false);
        image_index += 1;
        render_question(image_index);
        state += 1;
        update_header_buttons(state);
    }
    else if ( state >= 7 && state < 11){
        // was q 5 - 8, start q 6 - 9
        let ans = $('#description').val();
        record_answers(ans, image_index);
        state += 1;
        image_index += 1
        render_question(image_index);
        update_header_buttons(state);
    }else{
        let ans = $('#description').val();
        record_answers(ans, image_index);
        if (!finish()){
            return -1;
        }
    }
}


function start(){
    state = -1;
    $("#circles").prop('hidden', false);
    $("#images_speech").prop('hidden', true);
    $("#instructions_speech").prop('hidden', true);
    $("#instructions_written").prop('hidden', true);
    $("#finish").prop('hidden', true);
    update_header_buttons(state);
}

function finish(){
    for (i=0; i < questions.length; i++){
        if (questions[i].done === false){
            render_dialog(9);
            return false;
        }
    }
    $("#images_written").prop('hidden', true);
    $("#instructions").prop('hidden', true);
    $("#finish").prop('hidden', false);
    state += 1;
    update_header_buttons(state);
    $("#dialog-confirm" ).dialog('open');
}



function record_answers(ans, local_state){
    var q = questions[local_state];
    // store user input
    q.ans = ans;
    // Save time
    rn = new Date().getTime();
    q.time += rn - start_time;
    q.done = true;
    q.end_time = rn;
}


function check_correct(ans, local_state){
    if (ans.split(/\s+/).length < 8){
        render_dialog(7);
        return false;
    } else if (!check_new_answer(ans, questions)){
        render_dialog(1);
        return false;
    } else {
        record_answers(ans, local_state);
        return true;
    }
}

function check_new_answer(new_answer, descriptions){
    new_answer = new_answer.split(/[^a-z]/i).filter(function(i){return i}).map(name => name.toLowerCase());
    var desc = [];
    loop1:
    for(var i = 0; i < descriptions.length; i+=1){
        if(i === state){continue loop1;}
        desc = descriptions[i].ans.split(/[^a-z]/i).filter(function(i){return i}).map(name => name.toLowerCase());
        if(new_answer.length !== desc.length){continue loop1;}
        loop2:
        for(var j=0; j<desc.length; j+=1){
            if(new_answer[j] !== desc[j]){continue loop1;}
        }
        return false;
    }
    return true;
}


function check_all_checks(){
    if ($(".instruction-check:checked").length > 4) {
        $(".start-btn").prop("disabled", false);
    }
}

// ===============================================================
// CALIBRATION
// ==============================================================

function start_calibration(){
    cal_start = new Date().getTime();
    $("#circle").prop('hidden', false);
    $("#main-body").prop('hidden', true);
    $("#circles-instructions").prop('hidden', true)
    setTimeout(function(){
        cal_end = new Date().getTime();
        calibrations.push({
            start: cal_start,
            end: cal_end
        })
        $("#main-body").prop('hidden', false);
        $("#circles-instructions").prop('hidden', false)
        $("#circle").prop('hidden', true);
        $("#circles").prop('hidden', true);
        $("#instructions").prop('hidden', true);
        $("#finish").prop('hidden', true);
        next();
      }, 3000);
}


// ===============================================================
// rednering question, image, and dialog
// ==============================================================
function render_header_button(im_urls){
    $( "#button-header-group" ).append(`<button type="button" id="inst" class="header-btn btn btn-outline-secondary" disabled>Instructions 1</button>`);
    $( "#button-header-group" ).append(`<button type="button" id="calibrate-1" class="header-btn btn btn-outline-secondary" disabled>Calibration 1</button>`);
    for (var i=1; i <= 5; i++){
        $( "#button-header-group" ).append(`<button type="button" id="image-${i}" class="header-btn btn btn-outline-secondary" disabled>Image ${i}</button>`);
    }
    $( "#button-header-group" ).append(`<button type="button" id="inst" class="header-btn btn btn-outline-secondary" disabled>Instructions 2</button>`);
    $( "#button-header-group" ).append(`<button type="button" id="calibrate-2" class="header-btn btn btn-outline-secondary" disabled>Calibration 2</button>`);
    for (var i=6; i <= 10; i++){
        $( "#button-header-group" ).append(`<button type="button" id="image-${i}" class="header-btn btn btn-outline-secondary" disabled>Image ${i}</button>`);
    }
    $( "#button-header-group" ).append(`<button type="button" id="fin" class="header-btn btn btn-outline-secondary" disabled>Finish</button>`);
}

function render_question(idx){
    q = questions[idx]
    render_im(q.im);
    $(".next").prop("disabled", true);
    $('.state-button').show();
    $('#description').show();
    $('#description').css('width', 480);
    $('#description').css('height', 150);
    $('#description').val(q.ans);
    rn = new Date().getTime();
    start_time = rn;
    q.start_time = rn;
}

function render_im(im){
    var c = canvas[0]
    c.width = im.width;
    c.height = im.height;
    if (im.width > WINDOW_WIDTH * .47){
        // c.width =  WINDOW_WIDTH * .5;
        // c.height = im.height * WINDOW_WIDTH * .5 / im.width;
        c.height = im.height * WINDOW_WIDTH * .47 / im.width
        c.width = WINDOW_WIDTH * .47;
        im.height = c.height;
        im.width = c.width;
    }
    var ctx=c.getContext("2d");
    ctx.drawImage(im, 0, 0, c.width, c.height);
    window.scrollTo(0, document.body.scrollHeight);
}

function update_header_buttons(activeIdx){
    $( ".header-btn" ).each(function( index ) {
        if (index === activeIdx + 1){
            $(this).removeClass("btn-success").addClass("btn-outline-success");
        }
        if (index === activeIdx + 2){
            $(this).removeClass("btn-outline-secondary").addClass("btn-success");
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
        var text = 'Please provide different descriptions for each image.';
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
    var blobs = [];
    for (var i=0; i<5; i++){
        answers.push({
            im_url: questions[i].im.src,
            im_time: questions[i].time,
            im_start_time: questions[i].start_time,
            im_end_time: questions[i].end_time,
            im_height: questions[i].im.height,
            im_width: questions[i].im.width
        });
        blobs.push(questions[i].ans)
    }
    for (var i=5; i<10; i++){
        answers.push({
            im_url: questions[i].im.src,
            im_time: questions[i].time,
            im_start_time: questions[i].start_time,
            im_end_time: questions[i].end_time,
            im_height: questions[i].im.height,
            im_width: questions[i].im.width,
            description: questions[i].ans
        });
    }
    return [answers, blobs];
}