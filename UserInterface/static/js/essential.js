var start_time = new Date().getTime();

// ============================================================================
// initialize images
// ============================================================================
function initialize_images(im_urls) {
    for (var i = 0; i < im_urls.length; i++) {
        var im = new Image();
        var q = new Object();
        im.src = im_urls[i];
        q.im = im;
        q.ans = '';
        q.done = false;
        q.time = 0;
        // TODO: add fields for identifying images here
        questions.push(q);
    }
}

// ================================================================
// function to control next and previous question
// ===============================================================
function next(){
    let ans = $('#description').val();
    if (ans.length > 0){
        var q = questions[state];
        // store user input
        q.ans = ans;
        // Save time
        q.time += new Date().getTime() - start_time;
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
        // Save time
        q.time += new Date().getTime() - start_time;
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
            // Save time
            q.time += new Date().getTime() - start_time;
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
    if (question.ans.split(/\s+/).length < 8){
        render_dialog(7);
        return false;
    } else if (!check_new_answer(question.ans, questions)){
        render_dialog(1);
        return false;
    } else {
        question.done = true;
        return true;
    }
}

function check_new_answer(new_answer, descriptions){
    new_answer = new_answer.split(/[^a-z]/i).filter(function(i){return i}).map(name => name.toLowerCase());
    var desc = [];
    for(var i = 0; i < descriptions.length; i+=1){
        desc = descriptions[i].ans.split(/[^a-z]/i).filter(function(i){return i}).map(name => name.toLowerCase());
        if(new_answer.length !== desc.length){return false;}
        for(var j=0; j<desc.length; j+=1){
            if(new_answer[j] !== desc[j]){return false;}
        }
    }
    return true;
}

function check_all_checks(){
    if ($(".instruction-check:checked").length > 4) {
        $("#start-btn").prop("disabled", false);
    }
}
// ===============================================================
// rednering question, image, and dialog
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
    q = questions[idx]
    render_im(q.im);
    $('.state-button').show();
    $('#description').show();
    $('#description').css('width', 480);
    $('#description').css('height', 150);
    $('#description').val(q.ans);
    start_time = new Date().getTime();
}

function render_im(im){
    im.height = im.height * 480 / im.width
    im.width = 480;
    var c = $('#canvas')[0]
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
        });
    }
    return answers;
}
