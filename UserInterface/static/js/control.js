// ============================================================================
// create question set and state to go through the questions
// ============================================================================
var worker_obj = new Object();
var calibrations = new Array();
var state = -1;
jQuery.support.cors = true;
var questions = new Array();

var start_time = new Date().getTime();

var WINDOW_WIDTH = $(window).width();

// ============================================================================
// initialize images
// ============================================================================
function initialize_images(im_urls){
    for (var i=0; i < im_urls.length; i++){
        var im = new Image();
        var q = new Object();
        im.src = im_urls[i];
        q.im = im;
        q.ans = '';
        q.done = false;
        q.time = 0;
        q.start_time = 0;
        q.end_time = 0;
        questions.push(q);
    }
}

// ================================================================
// function to control next and previous question
// ===============================================================
function next(){
    if (state === -1) {
        // Was calibrating, start q 0
        state += 1;
        render_question(state);
        update_header_buttons(state);
    }
    else if (state === 0 || state === 1) {
        // Was q state, start q state + 1
        let ans = $('#description').val();
        if (!check_correct(ans, state)){
            return -1;
        }
        state += 1;
        render_question(state);
        update_header_buttons(state);
    }    
    else if (state === 2) {
        // Was q 2, start calibrating
        let ans = $('#description').val();
        if (!check_correct(ans, state)){
            return -1;
        }
        state += 1
        $("#circles").prop('hidden', false);
        $("#images").prop('hidden', true);
        $("#instructions").prop('hidden', true);
        $("#finish").prop('hidden', true);
        update_header_buttons(state);
    }
    else if (state === 3){
        // Was calibrating, start q 3
        render_question(state);
        state += 1;
        update_header_buttons(state);
    }
    else if ( state == 4 || state == 5){
        // was q 3 or 4, start q 4 or 5
        let ans = $('#description').val();
        if (!check_correct(ans, state - 1)){
            return -1;
        }
        state += 1;
        render_question(state - 1);
        update_header_buttons(state);
    }else{
        let ans = $('#description').val();
        if (!check_correct(ans, state - 1)){
            return -1;
        }
        // was last question, am I done?
        if (!finish()){
            return -1;
        }
    }
}


function start(){
    state = -1;
    $("#circles").prop('hidden', false);
    $("#images").prop('hidden', true);
    $("#instructions").prop('hidden', true);
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
    $("#images").prop('hidden', true);
    $("#instructions").prop('hidden', true);
    $("#finish").prop('hidden', false);
    state += 1;
    update_header_buttons(state);
    $("#dialog-confirm" ).dialog('open');
}

function check_correct(ans, local_state){
    if (ans.split(/\s+/).length < 8){
        render_dialog(7);
        return false;
    } else if (!check_new_answer(ans, questions)){
        render_dialog(1);
        return false;
    } else {
        var q = questions[local_state];
        // store user input
        q.ans = ans;
        // Save time
        rn = new Date().getTime();
        q.time += rn - start_time;
        q.done = true;
        q.end_time = rn;
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
    if ($(".instruction-check:checked").length > 5) {
        $("#start-btn").prop("disabled", false);
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
        $("#images").prop('hidden', false);
        $("#instructions").prop('hidden', true);
        $("#finish").prop('hidden', true);
        next();
      }, 3000);
}


// ===============================================================
// rednering question, image, and dialog
// ==============================================================
function render_header_button(im_urls){
    $( "#button-header-group" ).append(`<button type="button" id="inst" class="header-btn btn btn-outline-secondary" disabled>Instructions</button>`);
    $( "#button-header-group" ).append(`<button type="button" id="calibrate-1" class="header-btn btn btn-outline-secondary" disabled>Calibration 1</button>`);
    for (var i=1; i <= 3; i++){
        $( "#button-header-group" ).append(`<button type="button" id="image-${i}" class="header-btn btn btn-outline-secondary" disabled>Image ${i}</button>`);
    }
    $( "#button-header-group" ).append(`<button type="button" id="calibrate-2" class="header-btn btn btn-outline-secondary" disabled>Calibration 2</button>`);
    for (var i=4; i <= 6; i++){
        $( "#button-header-group" ).append(`<button type="button" id="image-${i}" class="header-btn btn btn-outline-secondary" disabled>Image ${i}</button>`);
    }
    $( "#button-header-group" ).append(`<button type="button" id="fin" class="header-btn btn btn-outline-secondary" disabled>Finish</button>`);
}

function render_question(idx){
    q = questions[idx]
    render_im(q.im);
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
    im.width = im.width * $(window).height() * .8 / im.height;
    im.height = $(window).height() * .8;
    // im.height = im.height * 480 / im.width
    // im.width = 480;
    var c = $('#canvas')[0]
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
    for (var i=0; i<questions.length; i++){
        answers.push({
            description: questions[i].ans,
            im_url: questions[i].im.src,
            im_time: questions[i].time,
            im_start_time: questions[i].start_time,
            im_end_time: questions[i].end_time,
            im_height: questions[i].im.height,
            im_width: questions[i].im.width
        });
    }
    return answers;
}